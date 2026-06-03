"""
Phase decomposition and quality scoring for workflow trajectories.

Companion to scoring.py. Handles task-specific phase judgment, per-campaign
correctness checks, and artifact quality scoring for W4.

Public functions:
  - call_w4_phase_judge(traj) -> dict
      Score one W4 trajectory on 5 phases (method appropriateness).
  - score_w4_correctness(traj, ground_truth) -> dict
      Deterministic per-campaign numeric correctness check.
  - score_w4_artifact_quality(traj) -> dict
      LLM judge for substantive quality: method-data fit, uncertainty
      discipline, numerical consistency, actionability.
  - score_w4_phases_batch(config_name) -> DataFrame
      Score all W4 trajectories on phases only.
  - score_w4_full_batch(config_name) -> DataFrame
      Score all W4 trajectories on phases + correctness + quality + trajectory
      shape. Workhorse for before/after intervention comparison.
  - calibrate_w4_phase_judge(hand_labels) -> dict
      Compare phase judge to hand-labels; report per-phase kappa.
  - chain_probability(phase_df) -> dict
      Compute marginal and conditional probabilities from a phase-scored df.

Cache:
  Judge results are cached in runs/_judge_cache/ keyed by content hash.
  Cache keys include rubric version strings; bumping a rubric version
  auto-invalidates old cached results.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Optional


# ============================================================
# Ground truth for W4 correctness scoring
# ============================================================

W4_GROUND_TRUTH = {
    "C001": {
        "true_effect": 4.22,           # 15% x $28.11 baseline
        "tolerance": 1.50,
        "method": "A/B test / t-test",
        "naive_estimate": None,
        "outcome_type": "continuous",
    },
    "C002": {
        "true_effect": 10.0,           # 5% x $200 treatment baseline
        "tolerance": 3.0,              # captures DiD (~$9.76) as correct
        "method": "matching / refuse / DiD-with-parallel-trends-verified",
        "naive_estimate": 145.0,       # naive cross-sectional comparison
        "naive_tolerance": 30.0,
        "outcome_type": "continuous",
    },
    "C003": {
        "true_effect": 3.15,           # 10% x $31.47 West baseline
        "tolerance": 1.50,
        "method": "DiD with parallel trends check",
        "naive_estimate": 6.88,
        "naive_tolerance": 1.5,
        "outcome_type": "continuous",
    },
    "C004": {
        "true_effect": 8.0,            # 8 percentage points
        "tolerance": 3.0,
        "method": "proportions test / chi-square on randomized",
        "naive_estimate": None,
        "outcome_type": "binary_pp",
    },
}


# ============================================================
# W4 phase judge rubric (5 phases, method-appropriateness focus)
# ============================================================

W4_PHASE_JUDGE_SYSTEM_PROMPT = """\
You are evaluating an AI agent's trajectory on a marketing campaign causal
analysis task (W4). The agent was given three files (campaigns.csv,
user_events.csv, users.csv) describing four marketing campaigns (C001 Spring
Email Blast, C002 Premium Upsell Push, C003 West Coast Regional, C004 Win-Back
Campaign). The agent's task was to recommend appropriate causal inference
methods per campaign and produce an analysis_plan.md.

You will score each of 5 phases as 1 (passed) or 0 (failed). Phases are
evaluated based on what is DEMONSTRATED in the deliverable (analysis_plan.md),
not the order the agent worked.

Return ONLY valid JSON in this exact format:
{
  "phase_1": <0 or 1>,
  "phase_2": <0 or 1>,
  "phase_3": <0 or 1>,
  "phase_4": <0 or 1>,
  "phase_5": <0 or 1>,
  "reasoning": {
    "phase_1": "<one sentence>",
    "phase_2": "<one sentence>",
    "phase_3": "<one sentence>",
    "phase_4": "<one sentence>",
    "phase_5": "<one sentence>"
  }
}

PHASE 1 - Data Loading
Did the agent successfully load all three required files and demonstrate
familiarity with their contents? Evidence: mentions of sample sizes (710
for C001, 144 for C002, 1000 for C003, 290 for C004), pre-campaign means,
or per-campaign data summaries.
Score 1 if the agent clearly engaged with all four campaigns' data.
Score 0 if any campaign is missing or data is clearly not loaded.

PHASE 2 - Assignment Diagnosis
Did the agent correctly identify the assignment mechanism for each campaign?
- C001: randomized A/B test
- C002: targeted / observational / non-randomized (selected for high spend)
- C003: geographic rollout / quasi-experimental
- C004: randomized A/B test
Score 1 if all four are correctly characterized.
Score 0 if any campaign is mischaracterized.

PHASE 3 - Bias Recognition
Did the agent explicitly flag the methodological problems:
- C002 has SELECTION BIAS: treatment group has much higher pre-campaign
  spend ($200 vs $65), so groups are not comparable.
- C003 has PARALLEL TRENDS concern or geographic-confounding issue.
Score 1 if BOTH concerns are explicitly named.
Score 0 if either is missing.

PHASE 4 - Method Recommendation (THE CRITICAL PHASE)

For each campaign, identify the specific method the agent recommended FOR
THAT CAMPAIGN'S section. Do NOT pattern-match on methods mentioned elsewhere.

For C001 (randomized): A/B test, t-test, DiD-on-randomized-data, proportions
test are ACCEPTABLE.

For C003 (geographic rollout): DiD, synthetic control, event study,
"insufficient pre-periods" are ACCEPTABLE.

For C004 (randomized binary): A/B test, chi-square, proportions test, DiD
on binary are ACCEPTABLE.

For C002 (selection-biased) - score carefully:

ACCEPTABLE for C002:
  - Refuses to estimate ("run a proper RCT", "data underidentified")
  - Propensity score matching
  - Inverse probability of treatment weighting (IPTW)
  - Regression adjustment / regression with controls
  - DiD + matching combined
  - Instrumental variables
  - Regression discontinuity at the $80 threshold

NOT ACCEPTABLE for C002:
  - Plain DiD as the headline method WITHOUT combining with matching or
    regression adjustment
  - Naive cross-sectional comparison reported as headline
  - DiD computed and "DiD is the answer" without additional adjustment

Score 1 if all four campaigns get an acceptable method.
Score 0 if any campaign - especially C002 - gets an unacceptable method.

IMPORTANT: Mentioning DiD as a framework concept, or applying DiD to a
randomized campaign (C001) where it's redundant but harmless, does NOT
count as failing C002. Only the method attached to C002's own analysis
matters for C002's score.

PHASE 5 - Deliverable Production
Did the agent produce a coherent analysis_plan.md that:
- Exists and is substantive (>800 characters)
- Discusses all four campaigns by ID (C001, C002, C003, C004)
- Provides a method recommendation for each campaign
- Gives an actionable investment recommendation per campaign

Score 1 if all four conditions met.
Score 0 otherwise.
"""


# ============================================================
# W4 artifact quality rubric (substantive, designed to discriminate)
# ============================================================

W4_QUALITY_JUDGE_SYSTEM_PROMPT = """\
You are evaluating the QUALITY of an AI agent's marketing campaign analysis
deliverable. You will score four SUBSTANTIVE dimensions, each on a 0-3 scale.

Critical scoring philosophy:
- A polished, well-structured document with shallow analysis is NOT high
  quality. Score it 1, not 3.
- Reserve 3s for deliverables that show genuine analytical depth, not just
  professional presentation.
- Be strict. Most boilerplate reports should score 1-2 on each dimension.
  Only deliverables with clear evidence of substantive engagement deserve 3s.

DIMENSION 1: METHOD-DATA FIT REASONING (0-3)
Does the agent explain WHY each method is appropriate for that specific
campaign's data structure?

0 = Methods are named but not justified. E.g., "We use DiD for C003" with
    no explanation.
1 = Generic justification ("DiD is standard for quasi-experiments") without
    engagement with this campaign's specific structure.
2 = Justification references the specific data (e.g., "DiD because C003 is
    a geographic rollout, requires parallel trends which we partially
    verified"), with at least one campaign treated with this depth.
3 = Each campaign's method is explicitly justified by reference to its
    assignment mechanism, the structure of the data, and the assumptions
    the method requires. Distinguishes verified vs. unverifiable assumptions.

DIMENSION 2: UNCERTAINTY DISCIPLINE (0-3)
Does the agent report effects with appropriate uncertainty quantification
and state what remains uncertain even after analysis?

0 = Point estimates only. Treats "p < 0.05" as proof of causation. No CI,
    no caveats about residual confounding.
1 = Some p-values or CIs reported but inconsistently. May confuse statistical
    significance with causal validity.
2 = CIs reported for most estimates. Distinguishes statistical from causal
    uncertainty. Names at least one residual confound.
3 = CIs reported for all estimates. Clearly distinguishes (a) sampling
    uncertainty, (b) selection-on-unobservables, (c) parallel trends
    violations, (d) external validity. For C002, acknowledges that EVEN
    with bias correction, the estimate has residual uncertainty.

DIMENSION 3: NUMERICAL CONSISTENCY (0-3)
Do numbers in executive summary, per-campaign sections, and budget tables
all agree?

0 = Numbers disagree across sections.
1 = Numbers mostly agree but confidence ratings or recommendations don't
    match the underlying analysis (e.g., flags C002 as biased then
    recommends scaling it).
2 = Numbers consistent. Confidence levels approximately match evidence.
3 = Fully consistent. Numerical estimates, confidence ratings, and
    recommendations form a coherent story.

DIMENSION 4: ACTIONABILITY OF RECOMMENDATIONS (0-3)
Are recommendations specific enough to act on, and do they reflect the
strength of evidence?

0 = Generic recommendations ("test more"). Or recommends scaling everything
    regardless of evidence quality.
1 = Concrete per-campaign recommendations but don't reflect differential
    confidence.
2 = Per-campaign recommendations that approximately reflect evidence quality.
3 = Recommendations tiered by evidence quality. Randomized (C001, C004) get
    "scale" with quantified expectations. Quasi-experimental (C003) gets
    "expand with validation steps named". Biased (C002) gets "do not scale;
    run an RCT first". Specific next steps for each tier.

CRITICAL ADDITIONAL RULES:

- If the agent does NOT report a numerical effect estimate for C002 (because
  they refused to analyze biased data), that is GOOD evidence of uncertainty
  discipline. Score Dimension 2 highly. Do NOT penalize on Dimension 4 for
  not having a C002 recommendation - refusing IS the recommendation.

- If the agent applies plain DiD to C002 and calls it "the answer," score
  Dimension 1 at most 1.

- If the agent reports the same effect for C002 (e.g., ~$9.76) in multiple
  sections but uses different terms ("DiD", "DiD+PSM", "matching") for it,
  score Dimension 3 at most 1.

- If the budget table contradicts the per-campaign analysis (e.g., flags
  C002 as biased then allocates 50% of budget to it), score Dimensions 3
  AND 4 at 0.

Return ONLY valid JSON in this format:
{
  "method_data_fit": <0-3>,
  "uncertainty_discipline": <0-3>,
  "numerical_consistency": <0-3>,
  "actionability": <0-3>,
  "total": <sum, 0-12>,
  "reasoning": {
    "method_data_fit": "<one sentence with specific evidence>",
    "uncertainty_discipline": "<one sentence with specific evidence>",
    "numerical_consistency": "<one sentence with specific evidence>",
    "actionability": "<one sentence with specific evidence>"
  }
}
"""


# ============================================================
# Phase judge prompt construction and call
# ============================================================

def _build_w4_phase_prompt(traj: dict) -> str:
    """Build user prompt with the analysis_plan.md content and artifact list."""
    artifact_dir = Path(traj["artifact_dir"])
    plan_path = artifact_dir / "analysis_plan.md"
    if plan_path.exists():
        plan_content = plan_path.read_text(encoding="utf-8", errors="replace")
    else:
        plan_content = "(analysis_plan.md not found)"

    final_answer = traj.get("final_answer", "")[:2000]

    artifact_list = []
    if artifact_dir.exists():
        for p in sorted(artifact_dir.iterdir()):
            if p.is_file() and p.name != "trajectory.json":
                artifact_list.append(f"  - {p.name} ({p.stat().st_size} bytes)")
    artifact_block = "\n".join(artifact_list) if artifact_list else "  (none)"

    return f"""\
=== ANALYSIS_PLAN.MD CONTENT ===
{plan_content}

=== AGENT'S FINAL ANSWER (first 2000 chars) ===
{final_answer}

=== ARTIFACTS PRODUCED ===
{artifact_block}

Score this trajectory on all 5 phases per the rubric. Return only JSON.
"""


def _phase_cache_path(traj: dict) -> Path:
    """Phase judge cache. v2 prefix invalidates older cached results."""
    plan_path = Path(traj["artifact_dir"]) / "analysis_plan.md"
    plan_hash = ""
    if plan_path.exists():
        plan_hash = hashlib.sha256(plan_path.read_bytes()).hexdigest()[:16]
    cache_key = (
        f"w4phase_v2_{traj['task_id']}_{traj['seed']}_"
        f"{traj['config_name']}_{plan_hash}"
    )
    cache_dir = Path("runs") / "_judge_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{hashlib.sha256(cache_key.encode()).hexdigest()[:16]}.json"


def call_w4_phase_judge(traj: dict,
                        judge_model: str = "claude-sonnet-4-5",
                        use_cache: bool = True) -> dict:
    """Score one W4 trajectory on 5 phases via LLM judge."""
    cache_path = _phase_cache_path(traj)
    if use_cache and cache_path.exists():
        try:
            with open(cache_path) as f:
                return json.load(f)
        except Exception:
            pass

    try:
        from anthropic import Anthropic
    except ImportError:
        return {
            "phase_1": 0, "phase_2": 0, "phase_3": 0, "phase_4": 0, "phase_5": 0,
            "reasoning": {"error": "anthropic SDK not installed"},
            "raw_response": "",
        }

    client = Anthropic()
    user_prompt = _build_w4_phase_prompt(traj)

    try:
        response = client.messages.create(
            model=judge_model,
            max_tokens=1500,
            system=W4_PHASE_JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        raw_clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw,
                           flags=re.MULTILINE)
        parsed = json.loads(raw_clean)
        result = {
            "phase_1": int(parsed["phase_1"]),
            "phase_2": int(parsed["phase_2"]),
            "phase_3": int(parsed["phase_3"]),
            "phase_4": int(parsed["phase_4"]),
            "phase_5": int(parsed["phase_5"]),
            "reasoning": parsed.get("reasoning", {}),
            "raw_response": raw,
        }
    except Exception as e:
        result = {
            "phase_1": 0, "phase_2": 0, "phase_3": 0, "phase_4": 0, "phase_5": 0,
            "reasoning": {"parse_error": f"{type(e).__name__}: {e}"},
            "raw_response": "",
        }

    try:
        with open(cache_path, "w") as f:
            json.dump(result, f)
    except Exception:
        pass

    return result


# ============================================================
# Correctness scoring (deterministic, no LLM)
# ============================================================

def _extract_campaign_effect(content: str, campaign_id: str) -> Optional[float]:
    """Pull the agent's reported effect for one campaign from analysis_plan.md."""
    section_match = re.search(
        rf"###?\s+(?:Campaign\s+)?{campaign_id}.*?(?=\n###?\s+(?:Campaign\s+)?C00[1-4]|\Z)",
        content, re.DOTALL | re.IGNORECASE
    )
    if not section_match:
        return None
    section = section_match.group(0)

    bolded = re.findall(r"\*\*\+?\$?([\d.]+)\s*(?:pp|per user)?\*\*", section)
    if bolded:
        try:
            return float(bolded[0])
        except ValueError:
            pass

    effect_patterns = [
        r"(?:effect|ATE|DiD|estimate|lift|treatment effect)[^\d]{0,40}\+?\$?([\d.]+)",
        r"\+?\$?([\d.]+)[^\d]{0,20}(?:per user|pp|percentage points|/user)",
    ]
    for pattern in effect_patterns:
        m = re.search(pattern, section, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                continue

    m = re.search(r"\$([\d.]+)", section)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass

    return None


def score_w4_correctness(traj: dict,
                         ground_truth: dict = W4_GROUND_TRUTH) -> dict:
    """Score numerical correctness of W4 agent's reported effects per campaign."""
    plan_path = Path(traj["artifact_dir"]) / "analysis_plan.md"
    if not plan_path.exists():
        return {"error": "no analysis_plan.md", "n_correct": 0, "n_total": 4}

    content = plan_path.read_text(encoding="utf-8", errors="replace")

    results = {}
    n_correct = 0
    matched_naive_on_c002 = False

    for campaign_id, gt in ground_truth.items():
        reported = _extract_campaign_effect(content, campaign_id)
        entry = {
            "reported": reported,
            "true_effect": gt.get("true_effect"),
            "tolerance": gt.get("tolerance"),
            "correct": None,
            "matched_naive": None,
        }

        if reported is None:
            entry["correct"] = False
            entry["note"] = "could not extract effect from section"
        elif gt.get("true_effect") is None:
            naive = gt.get("naive_estimate")
            naive_tol = gt.get("naive_tolerance", 1.0)
            if naive is not None:
                close_to_naive = abs(reported - naive) <= naive_tol
                entry["matched_naive"] = close_to_naive
                entry["correct"] = not close_to_naive
                if campaign_id == "C002" and close_to_naive:
                    matched_naive_on_c002 = True
            else:
                entry["correct"] = None
                entry["note"] = "no ground truth and no naive"
        else:
            true_val = gt["true_effect"]
            tol = gt["tolerance"]
            entry["correct"] = abs(reported - true_val) <= tol
            entry["delta"] = reported - true_val
            naive = gt.get("naive_estimate")
            naive_tol = gt.get("naive_tolerance", 1.0)
            if naive is not None and reported is not None:
                entry["matched_naive"] = abs(reported - naive) <= naive_tol
                if campaign_id == "C002" and entry["matched_naive"]:
                    matched_naive_on_c002 = True

        if entry["correct"] is True:
            n_correct += 1
        results[campaign_id] = entry

    results["n_correct"] = n_correct
    results["n_total"] = sum(1 for c in ground_truth.values()
                              if c.get("true_effect") is not None
                                 or c.get("naive_estimate") is not None)
    results["matched_naive_on_c002"] = matched_naive_on_c002
    return results


# ============================================================
# Artifact quality judge (LLM-based, substantive 4-dimension rubric)
# ============================================================

def _build_quality_prompt(traj: dict) -> str:
    """Build user prompt for the quality judge."""
    plan_path = Path(traj["artifact_dir"]) / "analysis_plan.md"
    plan_content = (plan_path.read_text(encoding="utf-8", errors="replace")
                    if plan_path.exists() else "(missing)")

    artifact_dir = Path(traj["artifact_dir"])
    artifact_list = []
    if artifact_dir.exists():
        for p in sorted(artifact_dir.iterdir()):
            if p.is_file() and p.name != "trajectory.json":
                artifact_list.append(f"  - {p.name}")
    artifact_block = "\n".join(artifact_list) if artifact_list else "  (none)"

    return f"""\
=== ANALYSIS_PLAN.MD ===
{plan_content}

=== OTHER ARTIFACTS PRODUCED ===
{artifact_block}

Evaluate the deliverable on the four substantive quality dimensions.
Be strict - most boilerplate deliverables should score 1-2 per dimension.
Reserve 3s for deliverables with genuine analytical depth.
Return only JSON.
"""


def _quality_cache_path(traj: dict) -> Path:
    """Quality cache. v2 prefix invalidates older cached results."""
    plan_path = Path(traj["artifact_dir"]) / "analysis_plan.md"
    plan_hash = ""
    if plan_path.exists():
        plan_hash = hashlib.sha256(plan_path.read_bytes()).hexdigest()[:16]
    cache_key = (
        f"w4quality_v2_{traj['task_id']}_{traj['seed']}_"
        f"{traj['config_name']}_{plan_hash}"
    )
    cache_dir = Path("runs") / "_judge_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{hashlib.sha256(cache_key.encode()).hexdigest()[:16]}.json"


def score_w4_artifact_quality(traj: dict,
                               judge_model: str = "claude-sonnet-4-5",
                               use_cache: bool = True) -> dict:
    """LLM judge for substantive artifact quality.

    Returns dict with four 0-3 scores on:
        method_data_fit, uncertainty_discipline, numerical_consistency,
        actionability
    plus total (0-12) and reasoning.
    """
    cache_path = _quality_cache_path(traj)
    if use_cache and cache_path.exists():
        try:
            with open(cache_path) as f:
                return json.load(f)
        except Exception:
            pass

    try:
        from anthropic import Anthropic
    except ImportError:
        return {
            "method_data_fit": 0, "uncertainty_discipline": 0,
            "numerical_consistency": 0, "actionability": 0, "total": 0,
            "reasoning": {"error": "anthropic SDK not installed"},
        }

    client = Anthropic()
    user_prompt = _build_quality_prompt(traj)

    try:
        response = client.messages.create(
            model=judge_model,
            max_tokens=2000,
            system=W4_QUALITY_JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        raw_clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw,
                           flags=re.MULTILINE)
        parsed = json.loads(raw_clean)
        result = {
            "method_data_fit": int(parsed["method_data_fit"]),
            "uncertainty_discipline": int(parsed["uncertainty_discipline"]),
            "numerical_consistency": int(parsed["numerical_consistency"]),
            "actionability": int(parsed["actionability"]),
            "total": int(parsed.get("total",
                                     parsed["method_data_fit"]
                                     + parsed["uncertainty_discipline"]
                                     + parsed["numerical_consistency"]
                                     + parsed["actionability"])),
            "reasoning": parsed.get("reasoning", {}),
        }
    except Exception as e:
        result = {
            "method_data_fit": 0, "uncertainty_discipline": 0,
            "numerical_consistency": 0, "actionability": 0, "total": 0,
            "reasoning": {"parse_error": f"{type(e).__name__}: {e}"},
        }

    try:
        with open(cache_path, "w") as f:
            json.dump(result, f)
    except Exception:
        pass

    return result


# ============================================================
# Calibration against hand labels
# ============================================================

def _cohen_kappa(y1: list, y2: list) -> Optional[float]:
    """Hand-rolled Cohen's kappa for binary raters."""
    n = len(y1)
    if n == 0:
        return None
    agree = sum(a == b for a, b in zip(y1, y2)) / n
    p1_pos = sum(y1) / n
    p2_pos = sum(y2) / n
    chance = p1_pos * p2_pos + (1 - p1_pos) * (1 - p2_pos)
    if chance >= 1.0:
        return 1.0
    return (agree - chance) / (1 - chance)


def calibrate_w4_phase_judge(hand_labels: dict,
                              runs_dir: Path = Path("runs"),
                              config_name: str = "baseline") -> dict:
    """Compare phase judge scores to hand labels."""
    judge_scores_by_phase = {f"phase_{k}": [] for k in range(1, 6)}
    hand_scores_by_phase = {f"phase_{k}": [] for k in range(1, 6)}
    disagreements = []

    for seed, hand_tuple in hand_labels.items():
        traj_path = (runs_dir / f"{config_name}__W4_campaign_analysis__seed{seed}"
                     / "trajectory.json")
        if not traj_path.exists():
            continue
        with open(traj_path) as f:
            traj = json.load(f)
        result = call_w4_phase_judge(traj, use_cache=True)

        for k in range(1, 6):
            phase = f"phase_{k}"
            judge_scores_by_phase[phase].append(result[phase])
            hand_scores_by_phase[phase].append(hand_tuple[k - 1])
            if result[phase] != hand_tuple[k - 1]:
                disagreements.append({
                    "seed": seed, "phase": phase,
                    "hand": hand_tuple[k - 1], "judge": result[phase],
                    "judge_reasoning": result["reasoning"].get(phase, ""),
                })

    per_phase_kappa = {}
    per_phase_agreement = {}
    for k in range(1, 6):
        phase = f"phase_{k}"
        judge_vals = judge_scores_by_phase[phase]
        hand_vals = hand_scores_by_phase[phase]
        if not judge_vals:
            per_phase_kappa[phase] = None
            per_phase_agreement[phase] = 0.0
            continue
        if (len(set(judge_vals)) == 1 and len(set(hand_vals)) == 1
                and judge_vals[0] == hand_vals[0]):
            per_phase_kappa[phase] = 1.0
        else:
            per_phase_kappa[phase] = _cohen_kappa(hand_vals, judge_vals)
        per_phase_agreement[phase] = sum(
            a == b for a, b in zip(judge_vals, hand_vals)
        ) / len(judge_vals)

    return {
        "n_trajectories": len([s for s in hand_labels if s is not None]),
        "per_phase_kappa": per_phase_kappa,
        "per_phase_agreement": per_phase_agreement,
        "disagreements": disagreements,
        "judge_scores_by_phase": judge_scores_by_phase,
        "hand_scores_by_phase": hand_scores_by_phase,
    }


# ============================================================
# Batch scoring (phases only) - lighter version
# ============================================================

def score_w4_phases_batch(config_name: str = "baseline",
                          runs_dir: Path = Path("runs"),
                          use_cache: bool = True):
    """Score all W4 trajectories on phases only. Returns DataFrame."""
    import pandas as pd

    rows = []
    pattern = f"{config_name}__W4_campaign_analysis__seed*"
    for run_dir in sorted(runs_dir.glob(pattern)):
        traj_path = run_dir / "trajectory.json"
        if not traj_path.exists():
            continue
        with open(traj_path) as f:
            traj = json.load(f)
        if traj.get("harness_error") or not traj.get("steps"):
            continue
        result = call_w4_phase_judge(traj, use_cache=use_cache)
        rows.append({
            "seed": traj["seed"],
            "config_name": traj["config_name"],
            "phase_1": result["phase_1"],
            "phase_2": result["phase_2"],
            "phase_3": result["phase_3"],
            "phase_4": result["phase_4"],
            "phase_5": result["phase_5"],
            "all_pass": int(all(result[f"phase_{k}"] for k in range(1, 6))),
            "phase_4_reason": result["reasoning"].get("phase_4", ""),
        })
    return pd.DataFrame(rows)


# ============================================================
# Full batch (phases + correctness + quality + trajectory shape)
# ============================================================

def _compute_redundancy_and_errors(steps: list) -> tuple:
    """Compute n_errors, n_redundant_calls, redundancy_rate, n_tool_calls."""
    n_errors = sum(1 for s in steps
                   if s.get("tool_result") and s["tool_result"].get("error"))

    seen = set()
    n_redundant = 0
    n_tool_calls = 0
    for s in steps:
        tc = s.get("tool_call")
        if not tc:
            continue
        n_tool_calls += 1
        code = tc.get("input", {}).get("code", "")
        norm_lines = []
        for line in code.split("\n"):
            if "#" in line:
                line = line[:line.index("#")]
            line = line.strip()
            if line:
                norm_lines.append(line)
        key = (tc["name"], "\n".join(norm_lines))
        if key in seen:
            n_redundant += 1
        else:
            seen.add(key)

    redundancy_rate = (n_redundant / n_tool_calls) if n_tool_calls else 0.0
    return n_errors, n_redundant, redundancy_rate, n_tool_calls


def score_w4_full_batch(config_name: str = "baseline",
                        runs_dir: Path = Path("runs"),
                        ground_truth: dict = W4_GROUND_TRUTH,
                        use_cache: bool = True):
    """Run all three scoring dimensions on all W4 trajectories for a config.

    Returns DataFrame with columns for:
      - Phase (phase_1..phase_5, all_phases_pass)
      - Correctness (correct_C001..correct_C004, matched_naive_on_c002)
      - Quality (method_data_fit, uncertainty_discipline,
                 numerical_consistency, actionability, quality_total)
      - Trajectory shape (total_steps, cost_usd, n_errors, n_redundant_calls,
                          redundancy_rate)
    """
    import pandas as pd

    rows = []
    pattern = f"{config_name}__W4_campaign_analysis__seed*"
    for run_dir in sorted(runs_dir.glob(pattern)):
        traj_path = run_dir / "trajectory.json"
        if not traj_path.exists():
            continue
        with open(traj_path) as f:
            traj = json.load(f)
        if traj.get("harness_error") or not traj.get("steps"):
            continue

        phase_result = call_w4_phase_judge(traj, use_cache=use_cache)
        correctness = score_w4_correctness(traj, ground_truth)
        quality = score_w4_artifact_quality(traj, use_cache=use_cache)

        steps = traj["steps"]
        n_errors, n_redundant, redundancy_rate, n_tool_calls = (
            _compute_redundancy_and_errors(steps)
        )

        cost = (traj["total_input_tokens"] * 3 / 1_000_000
                + traj["total_output_tokens"] * 15 / 1_000_000)

        rows.append({
            "seed": traj["seed"],
            "config_name": traj["config_name"],
            # Phase
            "phase_1": phase_result["phase_1"],
            "phase_2": phase_result["phase_2"],
            "phase_3": phase_result["phase_3"],
            "phase_4": phase_result["phase_4"],
            "phase_5": phase_result["phase_5"],
            "all_phases_pass": int(all(phase_result[f"phase_{k}"] for k in range(1, 6))),
            "phase_4_reason": phase_result["reasoning"].get("phase_4", ""),
            # Correctness
            "correct_C001": correctness.get("C001", {}).get("correct"),
            "correct_C002": correctness.get("C002", {}).get("correct"),
            "correct_C003": correctness.get("C003", {}).get("correct"),
            "correct_C004": correctness.get("C004", {}).get("correct"),
            "matched_naive_on_c002": correctness.get("matched_naive_on_c002", False),
            "n_correct": correctness.get("n_correct", 0),
            # Quality (new substantive rubric)
            "method_data_fit": quality["method_data_fit"],
            "uncertainty_discipline": quality["uncertainty_discipline"],
            "numerical_consistency": quality["numerical_consistency"],
            "actionability": quality["actionability"],
            "quality_total": quality["total"],
            # Trajectory shape
            "total_steps": len(steps),
            "n_tool_calls": n_tool_calls,
            "n_errors": n_errors,
            "n_redundant_calls": n_redundant,
            "redundancy_rate": redundancy_rate,
            "cost_usd": cost,
            "total_input_tokens": traj["total_input_tokens"],
            "total_output_tokens": traj["total_output_tokens"],
        })

    return pd.DataFrame(rows)


# ============================================================
# Chain probability decomposition
# ============================================================

def chain_probability(phase_df, n_phases: int = 5) -> dict:
    """Compute marginal and conditional phase probabilities."""
    n = len(phase_df)
    marginal = {}
    conditional = {}

    for k in range(1, n_phases + 1):
        marginal[k] = phase_df[f"phase_{k}"].mean()

    conditional[1] = marginal[1]
    for k in range(2, n_phases + 1):
        prior_cols = [f"phase_{j}" for j in range(1, k)]
        prior_passed = phase_df[phase_df[prior_cols].sum(axis=1) == (k - 1)]
        if len(prior_passed) == 0:
            conditional[k] = None
        else:
            conditional[k] = prior_passed[f"phase_{k}"].mean()

    chain_product = 1.0
    for k in range(1, n_phases + 1):
        if conditional[k] is None:
            chain_product = 0.0
            break
        chain_product *= conditional[k]

    all_cols = [f"phase_{k}" for k in range(1, n_phases + 1)]
    empirical_all_pass = (phase_df[all_cols].sum(axis=1) == n_phases).mean()

    return {
        "n": n,
        "marginal": marginal,
        "conditional": conditional,
        "chain_product": chain_product,
        "empirical_all_pass": empirical_all_pass,
    }