# Agent Evaluation: A Worked Example

This repo contains the code, data, and trajectory logs for a blog post on multi-axis evaluation of agentic workflows. It's a worked example showing that single-bit success/fail scoring hides most of what makes agent behavior interesting — and what makes it improvable.

**Blog post**: [link to your Substack/Medium post when published]

## What's in here

- **120 baseline trajectories** across 12 tasks (Q&A, workflow, gotcha) × 10 seeds, run with Claude Sonnet 4.5 at temperature 0
- **10 intervention trajectories** showing a 2-paragraph system prompt addition moves G1 (the impossible-forecast gotcha) from 0% → 80% success
- A scoring stack with three independent axes: outcome reliability, cost/trajectory shape, and trajectory quality via phase decomposition
- An LLM-judge-based phase decomposition framework applied to W4 (causal inference), with calibration against hand-labels
- Per-campaign correctness scoring against ground truth, plus a substantive artifact quality rubric

## The headline finding

W4 (causal campaign analysis) scores **100% under outcome-only scoring**. Under phase-decomposed scoring, the same trajectories fail 30–70% of the time depending on rubric strictness. The entire gap is concentrated in one phase: choosing the right causal method for the selection-biased campaign (C002). Agents recognize the bias, write about the bias, then apply plain DiD anyway.

G1 (forecast 6 months from 6 days of data) shows the opposite pattern. Baseline agents named the limitation and produced the forecast anyway (Hedged Delivery, 9/10 seeds). A two-paragraph addition to the system prompt giving the agent an explicit refusal protocol moved this to 8/10 clean refusals, with cost per trajectory dropping ~54% in the process.

## Repo structure

```
.
├── agent.py                    # Agent harness (persistent IPython kernel, sandboxed /tmp)
├── tasks.py                    # 12 task definitions with leak-safe ground truth
├── runner.py                   # Multi-seed runner with budget tracking and resumption
├── scoring.py                  # Outcome scoring: per-task rubrics + LLM judge for gotchas
├── phase_scoring.py            # W4 phase decomposition, correctness, quality (LLM judges)
├── generate_datsets.py         # Deterministic dataset generation (seed 42)
├── animated_charts.py          # Plotly charts for the blog post
│
├── data/                       # Generated CSVs (sales, users, sensors, campaigns, etc.)
├── _grading/                   # Ground truth for W4 campaign effects
├── runs/                       # 130 trajectory logs (baseline + calibration_v1)
│
├── analysis.ipynb              # Jupyter notebook tying everything together
├── results_all_tasks.csv       # Aggregated scoring across all 12 tasks
├── results_w4_phase_decomp.csv # W4 phase + correctness + quality scoring
│
├── chart1_cost_accumulation.html
├── chart2_artifact_variance.html
├── chart3_phase_waterfall.html
├── g1_before_after.png
└── trajectory_variance.png
```

## How to reproduce

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/agent-eval-blog.git
cd agent-eval-blog

# Create venv and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install anthropic pandas matplotlib plotly jupyter ipykernel python-dotenv

# Add your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Generate datasets

```bash
python generate_datsets.py
```

Produces deterministic CSVs in `data/` from seed 42.

### Run the baseline

```python
from runner import run_baseline
from agent import BASELINE_CONFIG
from tasks import ALL_TASKS

# Full baseline: 12 tasks × 10 seeds = 120 trajectories, ~$26
run_baseline(BASELINE_CONFIG, ALL_TASKS, n_seeds=10, max_budget_usd=50)
```

Trajectories save to `runs/baseline__<task_id>__seed<N>/`. The runner is resumable — re-running skips completed trajectories.

### Run the G1 intervention

```python
from agent import CALIBRATION_INTERVENTION_CONFIG

g1_task = [t for t in ALL_TASKS if t.task_id == "G1_short_forecast"]
run_baseline(CALIBRATION_INTERVENTION_CONFIG, g1_task, n_seeds=10, max_budget_usd=5)
```

### Score everything

```python
from runner import aggregate_results
from phase_scoring import score_w4_full_batch

# All-task outcome scoring (triggers LLM judge on gotchas, ~$0.06 first run)
df = aggregate_results()

# W4 phase decomposition + correctness + quality
df_w4 = score_w4_full_batch("baseline")
```

LLM judge results are cached in `runs/_judge_cache/` so re-running scoring is free.

## Methodology in brief

### Three evaluation axes

**1. Outcome reliability** — Task-type-specific scoring.
- Q&A: relative tolerances (e.g., ±15%), each documented with justification
- Workflow: artifact existence + content checks (keywords, structure) + integrity checks (no corrupted files, no input overwrites)
- Gotcha: LLM judge on a 3-point rubric (clean refusal / hedged delivery / no pushback), calibrated against hand-labels

**2. Cost & trajectory shape** — Per-trajectory: cost, steps, tool calls, errors, redundancy (same tool call twice with identical normalized code). Task-agnostic.

**3. Phase decomposition** (W4 only) — Five sequential phases scored by LLM judge:
1. Data Loading
2. Assignment Diagnosis
3. Bias Recognition
4. Method Recommendation
5. Deliverable Production

Chain probability: P(success) = ∏ P(phase_k | all earlier phases passed). Conditional probabilities surface which phase agents drop out at.

Plus two additional W4 dimensions:
- **Deterministic correctness** against ground truth (`_grading/ground_truth_campaigns.csv`)
- **Artifact quality** LLM judge on four substantive dimensions: method-data fit, uncertainty discipline, numerical consistency, actionability

### LLM judge instability (a known limitation)

Three runs of the W4 phase 4 judge on the same trajectories at temperature 0 gave 7/10, 0/10, and 6/10 pass rates respectively (depending on rubric strictness). Multi-judge consensus is on the future-work list. This is documented honestly in the post rather than hidden.

## Citations

- Jimenez et al., *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* (ICLR 2024, arXiv:2310.06770) — two-axis F2P/P2P scoring vocabulary
- Zheng et al., *Judging LLM-as-a-Judge with MT-Bench* (NeurIPS 2023, arXiv:2306.05685) — LLM judge calibration against hand-labels
- Lightman et al., *Let's Verify Step by Step* (arXiv:2305.20050) — process reward models for step-level evaluation
- Stroebl et al., *HAL: Holistic Agent Leaderboard* (arXiv:2510.11977) — outcome and cost as separate evaluation axes
- Cemri et al., *MAST: Multi-Agent System failure Taxonomy* (arXiv:2503.13657) — agent failure mode classification
- Miller et al., *Adding Error Bars to Evals* (Anthropic 2024, arXiv:2411.00640) — variance in LLM evaluation
- *Defeating Nondeterminism in LLM Inference* (Thinking Machines, Sept 2025) — judge reproducibility at temperature 0

## Future work

- Multi-judge consensus for phase scoring stability
- Apply the intervention to G2 (currently 100% Empty Answer due to infinite exploration)
- Extend phase decomposition to non-causal-inference workflows
- Multi-model comparison (currently single model: Claude Sonnet 4.5)

## License

MIT.

## Contact

Shradha Kaushal — [https://www.linkedin.com/in/shradha-kaushal/]
