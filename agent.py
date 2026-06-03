"""
Agent harness for the agent evaluation worked example.

Runs a single agent trajectory for a (task, seed, config) tuple and logs
everything to a JSON file. The agent has access to a Python execution tool
backed by a persistent IPython kernel (so state survives across tool calls,
which is how real production code-execution tools work).

Sandboxing: the IPython kernel is started with its cwd set to a /tmp/
working directory preloaded with only the required data files, so the
agent cannot read project source files.
"""

import json
import os
import queue
import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv
from jupyter_client import KernelManager

from tasks import Task

load_dotenv()
client = anthropic.Anthropic()


# ============================================================
# Configuration
# ============================================================

@dataclass
class AgentConfig:
    name: str
    model: str = "claude-sonnet-4-5"
    system_prompt: str = ""
    max_steps: int = 20
    max_tokens_per_turn: int = 4096
    temperature: float = 0.0

    # Safety limits
    max_total_tokens: int = 500_000
    max_wall_clock_seconds: int = 900


def config_for_task(base_config: AgentConfig, task) -> AgentConfig:
    """
    Return a copy of base_config with limits adjusted for the task type.
    Workflow tasks need more headroom — they produce long deliverables.
    Preserves system_prompt and other fields from base_config.
    """
    from dataclasses import replace

    if task._task_type == "workflow":
        return replace(
            base_config,
            max_steps=30,
            max_tokens_per_turn=8192,        # was 4096 — needed for long markdown
            max_total_tokens=500_000,
            max_wall_clock_seconds=900,
        )
    else:  # qa, gotcha
        return replace(
            base_config,
            max_steps=20,
            max_tokens_per_turn=4096,
            max_total_tokens=200_000,
            max_wall_clock_seconds=300,
        )


BASELINE_CONFIG = AgentConfig(
    name="baseline",
    system_prompt=(
        "You have access to a Python execution tool "
        "with a persistent kernel — variables and imports from earlier tool "
        "calls remain available in later ones. Use it to produce results by perfoming analysis. "
        "When you have a final answer or have "
        "completed the requested deliverable, state it clearly without making "
        "further tool calls."
    ),
)


# ============================================================
# Calibration intervention
# ============================================================
# Intervention for the Hedged Delivery failure mode observed on G1 baseline:
# the agent acknowledges insufficient data but produces the forecast anyway.
# This addition gives the agent an explicit refusal protocol for tasks that
# cannot be answered reliably with the data provided.

CALIBRATION_INTERVENTION_PROMPT_ADDITION = """

## When the task cannot be answered with the data given

Some tasks are impossible to answer reliably with the data you've been given.
When that's the case, your job is to recognize this and explain it clearly.
DO NOT produce a confident-looking deliverable with caveats.

A task is "underspecified" when any of the following is true:

1. The data lacks the columns or fields needed to answer the question
   (e.g., asked about marketing campaigns but no campaign column exists).
2. There are too few observations to support the requested analysis
   (e.g., forecasting 6 months ahead from 6 days of historical data).
3. The data has a structural problem that makes the analysis invalid
   (e.g., asked for a causal effect but groups are not comparable).

When you identify an underspecified task, you MUST:

- State clearly that the task as posed cannot be answered reliably.
- Explain the specific structural reason (which column is missing, how
  few observations there are, what assumption is violated).
- Describe what data WOULD be needed to answer the question properly.
- Suggest the right next step (collect more data, run a proper experiment,
  reformulate the question).

You MUST NOT:

- Produce a forecast, effect estimate, or recommendation that pretends the
  analysis is sound.
- Bury the limitation in a caveats section while still delivering the
  requested deliverable as if it were valid.
- Use phrases like "with appropriate caution" or "approximate estimate"
  to make an unsupportable analysis look defensible.

A short, clear refusal note IS the deliverable when the task is
underspecified. The fact that the task was asked does not obligate you to
produce a numeric answer. Producing the wrong answer confidently is worse
than refusing.

If you are confident the task IS answerable with the given data, proceed
normally. This guidance applies only when you encounter a structural
impossibility, not for routine tasks.
"""


CALIBRATION_INTERVENTION_CONFIG = AgentConfig(
    name="calibration_v1",
    model=BASELINE_CONFIG.model,
    system_prompt=BASELINE_CONFIG.system_prompt + CALIBRATION_INTERVENTION_PROMPT_ADDITION,
    max_steps=BASELINE_CONFIG.max_steps,
    max_tokens_per_turn=BASELINE_CONFIG.max_tokens_per_turn,
    temperature=BASELINE_CONFIG.temperature,
    max_total_tokens=BASELINE_CONFIG.max_total_tokens,
    max_wall_clock_seconds=BASELINE_CONFIG.max_wall_clock_seconds,
)


# ============================================================
# Trajectory data structures (unchanged)
# ============================================================

@dataclass
class Step:
    step_index: int
    timestamp: float
    duration_seconds: float
    input_tokens: int
    output_tokens: int
    stop_reason: str
    response_text: str
    tool_call: Optional[dict] = None
    tool_result: Optional[dict] = None


@dataclass
class Trajectory:
    task_id: str
    seed: int
    config_name: str
    model: str
    start_time: float
    end_time: float = 0.0
    work_dir: str = ""
    artifact_dir: str = ""
    steps: list[Step] = field(default_factory=list)
    final_answer: str = ""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    artifacts_created: list[str] = field(default_factory=list)
    harness_error: Optional[str] = None

    def to_dict(self):
        return asdict(self)


# ============================================================
# Persistent IPython kernel for Python execution
# ============================================================

class PersistentPythonKernel:
    """
    Wraps a Jupyter kernel that persists across many tool calls.
    Variables and imports defined in one execute() call remain available
    in later ones — matching how production code execution tools work.
    """

    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.km = KernelManager()
        # Start the kernel with cwd=work_dir so all file ops are sandboxed.
        self.km.start_kernel(cwd=str(work_dir))
        self.client = self.km.client()
        self.client.start_channels()
        # Wait for kernel to be ready
        self.client.wait_for_ready(timeout=30)

    def execute(self, code: str, timeout: int = 60) -> dict:
        """
        Execute code in the persistent kernel. Returns a dict with:
          - output: combined stdout/display output
          - error: bool
          - error_type: exception class name if error
        """
        msg_id = self.client.execute(code)

        output_parts = []
        error_info = None
        execution_done = False
        start = time.time()

        while not execution_done:
            if time.time() - start > timeout:
                # Try to interrupt the kernel
                try:
                    self.km.interrupt_kernel()
                except Exception:
                    pass
                return {
                    "output": f"Execution exceeded {timeout}s timeout.",
                    "error": True,
                    "error_type": "Timeout",
                }

            try:
                msg = self.client.get_iopub_msg(timeout=1)
            except queue.Empty:
                continue

            # Only process messages from this execution
            if msg.get("parent_header", {}).get("msg_id") != msg_id:
                continue

            msg_type = msg["msg_type"]
            content = msg["content"]

            if msg_type == "stream":
                output_parts.append(content.get("text", ""))
            elif msg_type == "execute_result":
                data = content.get("data", {})
                if "text/plain" in data:
                    output_parts.append(data["text/plain"])
            elif msg_type == "display_data":
                data = content.get("data", {})
                if "text/plain" in data:
                    output_parts.append(data["text/plain"])
            elif msg_type == "error":
                ename = content.get("ename", "Error")
                evalue = content.get("evalue", "")
                traceback = "\n".join(content.get("traceback", []))
                # Strip ANSI color codes from traceback
                import re
                traceback = re.sub(r"\x1b\[[0-9;]*m", "", traceback)
                error_info = {
                    "error_type": ename,
                    "output": f"{traceback}\n{ename}: {evalue}",
                }
            elif msg_type == "status":
                if content.get("execution_state") == "idle":
                    execution_done = True

        if error_info:
            return {
                "output": error_info["output"][-4000:],
                "error": True,
                "error_type": error_info["error_type"],
            }

        output = "".join(output_parts)
        return {
            "output": output[-4000:] if output else "(no output)",
            "error": False,
            "error_type": None,
        }

    def shutdown(self):
        try:
            self.client.stop_channels()
        except Exception:
            pass
        try:
            self.km.shutdown_kernel(now=True)
        except Exception:
            pass


# Tool schema for the API
PYTHON_TOOL = {
    "name": "python",
    "description": (
        "Execute Python code in a persistent kernel. Variables and imports "
        "from previous calls remain available — you do not need to re-import "
        "or reload data unless you want to. The kernel's working directory "
        "contains the data files for this task. Use print() to show results; "
        "only printed output and expression values are returned to you. "
        "You can save files (PNGs via matplotlib's savefig, markdown via "
        "regular file writes, etc.) — these will be collected as your "
        "final deliverables."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute.",
            }
        },
        "required": ["code"],
    },
}


# ============================================================
# Sandbox setup and teardown (unchanged)
# ============================================================

def prepare_sandbox(task: Task, data_dir: Path = Path("data")) -> Path:
    work_dir = Path(tempfile.mkdtemp(prefix=f"agent_eval_{task.task_id}_"))
    for filename in task.required_files:
        src = data_dir / filename
        if not src.exists():
            raise FileNotFoundError(f"Required dataset missing: {src}")
        shutil.copy2(src, work_dir / filename)
    return work_dir


def collect_artifacts(work_dir: Path, artifact_dir: Path,
                      input_files: list[str]) -> list[str]:
    """
    Copy files the agent created (not the input CSVs) into a persistent
    artifact directory. Returns the list of artifact filenames.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    input_set = set(input_files)
    for f in work_dir.iterdir():
        if f.name in input_set:
            continue
        if f.name.startswith("."):
            continue
        shutil.copy2(f, artifact_dir / f.name)
        artifacts.append(f.name)
    return artifacts


# ============================================================
# The agent loop
# ============================================================

def run_agent(
    task: Task,
    config: AgentConfig,
    seed: int,
    runs_root: Path = Path("runs"),
) -> Trajectory:
    # Adjust limits based on task type (workflow tasks get more headroom).
    # config_for_task preserves system_prompt and other fields from the
    # input config — so passing CALIBRATION_INTERVENTION_CONFIG here works
    # without needing a separate task-aware variant.
    config = config_for_task(config, task)

    run_id = f"{config.name}__{task.task_id}__seed{seed}"
    artifact_dir = runs_root / run_id

    traj = Trajectory(
        task_id=task.task_id,
        seed=seed,
        config_name=config.name,
        model=config.model,
        start_time=time.time(),
        artifact_dir=str(artifact_dir),
    )

    work_dir = None
    kernel = None
    try:
        work_dir = prepare_sandbox(task)
        traj.work_dir = str(work_dir)
        kernel = PersistentPythonKernel(work_dir)

        messages = [{"role": "user", "content": task.to_prompt()}]

        for step_index in range(config.max_steps):
            step_start = time.time()

            # Safety check: total tokens used so far
            total_so_far = traj.total_input_tokens + traj.total_output_tokens
            if total_so_far > config.max_total_tokens:
                traj.harness_error = (
                    f"Aborted: exceeded max_total_tokens "
                    f"({total_so_far} > {config.max_total_tokens})"
                )
                break

            # Safety check: wall clock
            elapsed = time.time() - traj.start_time
            if elapsed > config.max_wall_clock_seconds:
                traj.harness_error = (
                    f"Aborted: exceeded max_wall_clock_seconds "
                    f"({elapsed:.0f}s > {config.max_wall_clock_seconds}s)"
                )
                break

            api_kwargs = {
                "model": config.model,
                "max_tokens": config.max_tokens_per_turn,
                "tools": [PYTHON_TOOL],
                "messages": messages,
                "temperature": config.temperature,
            }
            if config.system_prompt:
                api_kwargs["system"] = config.system_prompt

            response = client.messages.create(**api_kwargs)

            response_text = ""
            tool_call = None
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                elif block.type == "tool_use":
                    tool_call = {
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }

            step = Step(
                step_index=step_index,
                timestamp=step_start,
                duration_seconds=time.time() - step_start,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                stop_reason=response.stop_reason,
                response_text=response_text,
                tool_call=tool_call,
            )
            traj.total_input_tokens += response.usage.input_tokens
            traj.total_output_tokens += response.usage.output_tokens

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use" and tool_call:
                if tool_call["name"] == "python":
                    code = tool_call["input"].get("code", "")
                    if not code.strip():
                        # The agent tried to make a tool call but the input
                        # was truncated (typically because max_tokens hit
                        # mid-generation). Feed back a hint and continue.
                        tool_result = {
                            "output": (
                                "Your previous tool call had empty input — "
                                "likely because output token limit was hit "
                                "mid-generation. Try generating long content "
                                "in smaller chunks (write to a file in "
                                "multiple steps), or split your code across "
                                "multiple tool calls."
                            ),
                            "error": True,
                            "error_type": "EmptyToolInput",
                        }
                    else:
                        tool_result = kernel.execute(code)
                else:
                    tool_result = {
                        "output": f"Unknown tool: {tool_call['name']}",
                        "error": True,
                        "error_type": "UnknownTool",
                    }

                step.tool_result = tool_result
                traj.steps.append(step)

                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": tool_result["output"] or "(no output)",
                        "is_error": tool_result["error"],
                    }],
                })
                continue

            traj.steps.append(step)
            traj.final_answer = response_text.strip()
            break

    except Exception as e:
        traj.harness_error = f"{type(e).__name__}: {e}"

    finally:
        if kernel is not None:
            kernel.shutdown()

        if work_dir is not None and work_dir.exists():
            try:
                traj.artifacts_created = collect_artifacts(
                    work_dir, artifact_dir, task.required_files
                )
            except Exception as e:
                traj.harness_error = (
                    (traj.harness_error or "") + f" | collect_artifacts: {e}"
                )
            try:
                shutil.rmtree(work_dir)
            except Exception:
                pass

        traj.end_time = time.time()

        artifact_dir.mkdir(parents=True, exist_ok=True)
        log_path = artifact_dir / "trajectory.json"
        with open(log_path, "w") as f:
            json.dump(traj.to_dict(), f, indent=2, default=str)

    return traj