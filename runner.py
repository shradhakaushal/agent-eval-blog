"""
Multi-seed baseline runner for the agent evaluation worked example.

Loops over (task, config, seed) tuples, calling run_agent for each.
Handles rate limit backoff, cost tracking, and resumable runs.
Aggregates results into a pandas DataFrame for analysis.

Usage from the notebook:
    from runner import run_baseline, aggregate_results
    run_baseline(BASELINE_CONFIG, ALL_TASKS, n_seeds=10, max_budget_usd=50)
    df = aggregate_results()
"""

import json
import time
from pathlib import Path
from typing import Optional

import anthropic
import pandas as pd

from agent import AgentConfig, run_agent
from tasks import Task, ALL_TASKS
from scoring import score_trajectory, compute_trajectory_metrics


# ============================================================
# Cost model
# ============================================================

# Claude Sonnet 4.5 prices (USD per million tokens) — update if the model changes.
PRICE_PER_M_INPUT = 3.00
PRICE_PER_M_OUTPUT = 15.00


def estimate_trajectory_cost(input_tokens: int, output_tokens: int) -> float:
    """Return the cost in USD for one trajectory's token usage."""
    return (
        input_tokens * PRICE_PER_M_INPUT / 1_000_000
        + output_tokens * PRICE_PER_M_OUTPUT / 1_000_000
    )


# ============================================================
# Resumable: detect already-completed trajectories
# ============================================================

def trajectory_already_done(task: Task, config: AgentConfig, seed: int,
                            runs_root: Path = Path("runs")) -> Optional[dict]:
    """
    If a trajectory.json already exists for this (config, task, seed),
    return its parsed contents. Otherwise return None.
    """
    run_id = f"{config.name}__{task.task_id}__seed{seed}"
    log_path = runs_root / run_id / "trajectory.json"
    if not log_path.exists():
        return None
    try:
        with open(log_path) as f:
            return json.load(f)
    except Exception:
        # Corrupted file — treat as not done
        return None


# ============================================================
# Rate-limit-aware single trajectory run
# ============================================================

def run_with_retries(task: Task, config: AgentConfig, seed: int,
                     max_retries: int = 3) -> Optional[dict]:
    """
    Run a single trajectory with exponential backoff on rate limit errors.
    Returns the trajectory dict, or None if all retries failed.
    """
    delay = 30  # seconds for first retry
    for attempt in range(max_retries):
        try:
            traj = run_agent(task, config, seed)
            return traj.to_dict()
        except anthropic.RateLimitError as e:
            if attempt == max_retries - 1:
                print(f"  [RATE LIMIT] gave up after {max_retries} attempts: {e}")
                return None
            print(f"  [RATE LIMIT] backing off {delay}s before retry "
                  f"(attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
            delay *= 2
        except anthropic.APIError as e:
            # Transient API errors — retry once
            if attempt == max_retries - 1:
                print(f"  [API ERROR] gave up: {e}")
                return None
            print(f"  [API ERROR] retrying after 10s: {e}")
            time.sleep(10)
        except Exception as e:
            # Unexpected error — log and skip (don't retry)
            print(f"  [UNEXPECTED] {type(e).__name__}: {e} — skipping")
            return None
    return None


# ============================================================
# The main baseline run
# ============================================================

def run_baseline(
    config: AgentConfig,
    tasks: list[Task] = ALL_TASKS,
    n_seeds: int = 10,
    max_budget_usd: float = 50.0,
    runs_root: Path = Path("runs"),
    skip_existing: bool = True,
) -> dict:
    """
    Run `config` against every task in `tasks` for `n_seeds` seeds each.

    - Resumable: skips trajectories whose trajectory.json already exists.
    - Budget-bounded: aborts if cumulative cost exceeds max_budget_usd.
    - Rate-limit aware: retries with backoff on 429s.

    Returns a summary dict with cost, counts, and timings.
    """
    start_time = time.time()
    total_combinations = len(tasks) * n_seeds
    completed = 0
    skipped = 0
    failed = 0
    cumulative_cost = 0.0

    print(f"Starting baseline run: {config.name}")
    print(f"  Tasks: {len(tasks)}, Seeds: {n_seeds}, "
          f"Total trajectories: {total_combinations}")
    print(f"  Budget cap: ${max_budget_usd:.2f}")
    print(f"  Resume mode: {'on' if skip_existing else 'off'}")
    print("=" * 70)

    for task in tasks:
        for seed in range(n_seeds):
            idx = completed + skipped + failed + 1

            # Resume: skip if already done
            if skip_existing:
                existing = trajectory_already_done(task, config, seed, runs_root)
                if existing:
                    cost = estimate_trajectory_cost(
                        existing["total_input_tokens"],
                        existing["total_output_tokens"],
                    )
                    cumulative_cost += cost
                    skipped += 1
                    print(f"[{idx}/{total_combinations}] SKIP {task.task_id} "
                          f"seed={seed} (already done, ${cost:.2f})")
                    continue

            # Budget check
            if cumulative_cost > max_budget_usd:
                print(f"\n*** BUDGET STOP: ${cumulative_cost:.2f} > "
                      f"${max_budget_usd:.2f} ***")
                print(f"Completed {completed} new trajectories before stopping.")
                break

            # Run it
            t0 = time.time()
            print(f"[{idx}/{total_combinations}] RUN  {task.task_id} "
                  f"seed={seed} ...", end="", flush=True)
            result = run_with_retries(task, config, seed)
            duration = time.time() - t0

            if result is None:
                failed += 1
                print(f" FAILED ({duration:.0f}s)")
                continue

            cost = estimate_trajectory_cost(
                result["total_input_tokens"], result["total_output_tokens"]
            )
            cumulative_cost += cost
            completed += 1

            print(f" done ({duration:.0f}s, {len(result['steps'])} steps, "
                  f"${cost:.2f}, total=${cumulative_cost:.2f})")

        # Budget check at task boundary too
        if cumulative_cost > max_budget_usd:
            break

    elapsed = time.time() - start_time
    print("=" * 70)
    print(f"Baseline run finished in {elapsed/60:.1f} min")
    print(f"  Completed (new): {completed}")
    print(f"  Skipped (resumed): {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Total cost (incl. resumed): ${cumulative_cost:.2f}")

    return {
        "config_name": config.name,
        "n_tasks": len(tasks),
        "n_seeds": n_seeds,
        "completed": completed,
        "skipped": skipped,
        "failed": failed,
        "total_cost_usd": cumulative_cost,
        "elapsed_seconds": elapsed,
    }


# ============================================================
# Results aggregation
# ============================================================

def aggregate_results(
    runs_root: Path = Path("runs"),
    config_filter: Optional[str] = None,
) -> pd.DataFrame:
    """
    Walk runs/ and assemble one row per (task, seed, config) trajectory.
    Each row contains: identifiers, scoring fields, trajectory metrics, cost.

    Args:
        config_filter: if set, only include rows for this config name.

    Returns a pandas DataFrame.
    """
    rows = []
    task_lookup = {t.task_id: t for t in ALL_TASKS}

    if not runs_root.exists():
        print(f"No runs directory at {runs_root}")
        return pd.DataFrame()

    for run_dir in sorted(runs_root.iterdir()):
        if not run_dir.is_dir():
            continue
        log_path = run_dir / "trajectory.json"
        if not log_path.exists():
            continue

        try:
            with open(log_path) as f:
                traj = json.load(f)
        except Exception as e:
            print(f"  [skip] couldn't read {run_dir.name}: {e}")
            continue

        if config_filter and traj["config_name"] != config_filter:
            continue

        task = task_lookup.get(traj["task_id"])
        if task is None:
            print(f"  [skip] unknown task: {traj['task_id']}")
            continue

        # Score and metrics
        try:
            score = score_trajectory(traj, task)
            metrics = compute_trajectory_metrics(traj)
        except Exception as e:
            print(f"  [skip] scoring failed for {run_dir.name}: {e}")
            continue

        cost = estimate_trajectory_cost(
            traj["total_input_tokens"], traj["total_output_tokens"]
        )

        row = {
            # Identifiers
            "config_name": traj["config_name"],
            "task_id": traj["task_id"],
            "task_type": task._task_type,
            "task_difficulty": task._difficulty,
            "seed": traj["seed"],
            # Outcome
            "success": score.success,
            "extracted_answer": score.extracted_answer,
            "score_reason": score.score_reason,
            "outcome_category": score.outcome_category,
            "integrity_passed": score.integrity_passed,
            "integrity_failures": "; ".join(score.integrity_failures) if score.integrity_failures else "",
            "judge_score": score.judge_score,
            "judge_reason": score.judge_reason,
            # Cost
            "total_input_tokens": metrics.total_input_tokens,
            "total_output_tokens": metrics.total_output_tokens,
            "cost_usd": cost,
            "duration_seconds": metrics.total_duration_seconds,
            # Trajectory shape
            "total_steps": metrics.total_steps,
            "n_tool_calls": metrics.n_tool_calls,
            "n_reasoning_only_steps": metrics.n_reasoning_only_steps,
            "tokens_per_step": metrics.tokens_per_step,
            # Errors and recovery
            "n_errors": metrics.n_errors,
            "encountered_error": metrics.encountered_error,
            "consecutive_error_pairs": metrics.consecutive_error_pairs,
            "error_types": str(metrics.error_types),
            # Redundancy and termination
            "n_redundant_calls": metrics.n_redundant_calls,
            "redundancy_rate": metrics.redundancy_rate,
            "hit_max_steps": metrics.hit_max_steps,
            "harness_error": traj.get("harness_error"),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df