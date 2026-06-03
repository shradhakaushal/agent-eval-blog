"""
Task definitions for the agent evaluation worked example.

Each task has two clearly separated sets of fields:

1. AGENT-VISIBLE fields, returned by task.to_prompt():
   - The natural-language question/instructions

2. GRADING-ONLY fields, prefixed with underscore to mark them private:
   - _expected_answer: ground truth (for QA/gotcha tasks)
   - _answer_tolerance: how to score the answer
   - _accepted_aliases: alternative phrasings that should also be accepted
   - _expected_artifacts: required output files (for workflow tasks)
   - _task_type, _difficulty, _notes: metadata, NEVER in prompts

The harness must only call task.to_prompt() when building the agent's input.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    task_id: str
    question: str
    required_files: list[str]

    # Grading-only fields. Never include in the agent's prompt.
    _task_type: str = "qa"                           # "qa" | "workflow" | "gotcha"
    _expected_answer: Optional[str] = None
    _answer_tolerance: str = "exact_match"           # "exact_match" | "numeric:±X" | "refusal"
    _accepted_aliases: list[str] = field(default_factory=list)
    _expected_artifacts: list[str] = field(default_factory=list)
    _difficulty: str = "medium"
    _notes: str = ""

    def to_prompt(self) -> str:
        """Return ONLY the content shown to the agent."""
        files_str = ", ".join(self.required_files)
        return (
            f"You are working with data files in your current directory.\n"
            f"Available files: {files_str}\n\n"
            f"Load them using relative paths (e.g., pd.read_csv('sales.csv')).\n"
            f"Do not attempt to access files outside your current working directory.\n\n"
            f"Task: {self.question}"
        )


# ============================================================
# Tier 1: Q&A tasks (6 tasks)
# ============================================================

TASKS_QA = [
    Task(
        task_id="T1_top_region",
        question=(
            "Using the data in sales.csv, which region had the highest total "
            "revenue this year? Give your final answer as the region name."
        ),
        required_files=["sales.csv"],
        _task_type="qa",
        _expected_answer="West",
        _answer_tolerance="exact_match",
        _difficulty="easy",
        _notes=(
            "West has baseline revenue 25-50% higher than other regions. "
            "Margin of $748K over runner-up (East)."
        ),
    ),
    Task(
        task_id="T4_premium_active_spend",
        question=(
            "Using the data in users.csv, what is the average monthly spend "
            "of active users on the 'premium' plan tier? Give your final "
            "answer as a single number (USD)."
        ),
        required_files=["users.csv"],
        _task_type="qa",
        _expected_answer="62",
        _answer_tolerance="numeric:±10",
        _difficulty="medium",
        _notes=(
            "Population: 102 active premium users with valid spend. "
            "Strict mean: $62. Naive mean (without excluding negatives): $59.61. "
            "±$10 tolerance accommodates both interpretations."
        ),
    ),
    Task(
        task_id="T5_top_country",
        question=(
            "Using the data in users.csv, which country has the highest "
            "number of users? Give your final answer as a single country name."
        ),
        required_files=["users.csv"],
        _task_type="qa",
        _expected_answer="US",
        _accepted_aliases=["United States", "USA", "America"],
        _answer_tolerance="exact_match",
        _difficulty="medium",
        _notes=(
            "Without normalization: 'United States' has 291, 'US' has 287 (raw top). "
            "With normalization: US/United States combined has 578 (true top). "
            "Either US or United States is accepted as the right answer; "
            "any other country (e.g., 'UK') is wrong."
        ),
    ),
    Task(
        task_id="T6_median_2023_spend",
        question=(
            "Using the data in users.csv, among users who signed up in 2023, "
            "what is the median monthly spend, excluding users with negative "
            "spend values? Give your final answer as a single number (USD)."
        ),
        required_files=["users.csv"],
        _task_type="qa",
        _expected_answer="7.7",
        _answer_tolerance="numeric:±5",
        _difficulty="hard",
        _notes=(
            "Strict median: $7.65 (population dominated by free-tier users at $0). "
            "Tolerance ±$5 accommodates differences in date parsing and NaN handling."
        ),
    ),
    Task(
        task_id="T8_top_variance_sensor",
        question=(
            "Using the data in sensors.csv, which sensor had the most variable "
            "temperature readings (highest standard deviation) over the period? "
            "Give your final answer as a single sensor ID."
        ),
        required_files=["sensors.csv"],
        _task_type="qa",
        _expected_answer="sensor_3",
        _answer_tolerance="exact_match",
        _difficulty="medium",
        _notes=(
            "sensor_3 std = 3.38°C, all others around 0.30°C. "
            "Margin of 3.07°C — unmistakable."
        ),
    ),
Task(
    task_id="T9_germany_orders",
    question=(
        "Using the data in orders.csv, customers.csv, and order_items.csv, "
        "what is the average order total for customers from Germany? Give "
        "your final answer as a single number in USD."
    ),
    required_files=["orders.csv", "customers.csv", "order_items.csv"],
    _task_type="qa",
    _expected_answer="351",
    _answer_tolerance="numeric:±20",
    _difficulty="hard",
    _notes=(
        "Strict answer: $351 USD (Germany variants normalized, completed "
        "orders only, EUR→USD at 1.08). Naive answer: $325 (raw EUR, no "
        "filter). ±$20 tolerance cleanly separates the two methodologies."
    ),
),
]


# ============================================================
# Tier 2: Workflow tasks (3 tasks)
# ============================================================

TASKS_WORKFLOW = [
    Task(
        task_id="W1_sales_report",
        question=(
            "You have monthly sales data in sales.csv. Produce a brief report "
            "for a non-technical executive that summarizes how the business "
            "performed this year. Your deliverable should include:\n"
            "1. A clear narrative covering the top 2-3 findings\n"
            "2. At least one chart showing the trend that matters most\n"
            "3. One recommendation for what to focus on next quarter\n\n"
            "Save the chart as report_sales_chart.png and write the narrative "
            "as report_sales.md. Use language appropriate for a non-technical "
            "audience."
        ),
        required_files=["sales.csv"],
        _task_type="workflow",
        _expected_artifacts=["report_sales.md", "report_sales_chart.png"],
        _difficulty="medium",
        _notes="Tests multi-artifact output, audience-appropriate language.",
    ),
    Task(
        task_id="W2_segmentation",
        question=(
            "Using the data in users.csv, produce a customer segmentation report. "
            "Group users into meaningful tiers based on their activity and spending, "
            "then recommend which segments the company should prioritize for "
            "retention vs. growth investment.\n\n"
            "Your deliverable should include:\n"
            "1. A markdown report saved as report_segments.md\n"
            "2. At least one chart showing the segments\n"
            "3. A recommendation table or list\n\n"
            "Be thoughtful about data quality issues you encounter."
        ),
        required_files=["users.csv"],
        _task_type="workflow",
        _expected_artifacts=["report_segments.md"],
        _difficulty="hard",
        _notes=(
            "Tests handling of dirty data AND segmentation judgment AND "
            "multi-artifact output."
        ),
    ),
    Task(
        task_id="W3_anomaly_investigation",
        question=(
            "The sensors.csv data contains 30 days of readings from 5 sensors. "
            "We suspect one sensor may be malfunctioning. Investigate the data, "
            "identify any anomalous behavior, and produce a brief technical "
            "report explaining:\n"
            "1. Which sensor (if any) appears problematic\n"
            "2. What evidence supports that conclusion\n"
            "3. What you recommend\n\n"
            "Save the report as report_anomalies.md and include at least one "
            "supporting visualization saved as a PNG file."
        ),
        required_files=["sensors.csv"],
        _task_type="workflow",
        _expected_artifacts=["report_anomalies.md"],
        _difficulty="hard",
        _notes="Correct answer: sensor_3 (drifts upward starting day 15).",
    ),
    Task(
    task_id="W4_campaign_analysis",
    question=(
        "You have marketing campaign data and user event data. The marketing "
        "team wants to understand whether their campaigns are working and "
        "which ones to invest in next quarter.\n\n"
        "Your job: produce an analysis plan that explains how you would "
        "measure the causal impact of each campaign. For each campaign:\n"
        "1. Describe what kind of data we have (experimental, observational, etc.)\n"
        "2. Recommend an appropriate analytical method (A/B test analysis, "
        "difference-in-differences, matching, regression with controls, etc.)\n"
        "3. Flag any caveats or limitations of the proposed approach\n"
        "4. Where possible, provide preliminary estimates of campaign effects "
        "from the available data\n\n"
        "Save your analysis plan as analysis_plan.md and include any supporting "
        "visualizations as PNG files. The audience is a marketing director who "
        "wants actionable recommendations grounded in valid causal reasoning."
    ),
    required_files=["campaigns.csv", "user_events.csv", "users.csv"],
    _task_type="workflow",
    _expected_artifacts=["analysis_plan.md"],
    _difficulty="hard",
    _notes=(
        "Open-ended causal inference task. Four campaigns with different "
        "assignment structures: C001 randomized A/B, C002 targeted (selection "
        "bias), C003 geo rollout (parallel trends violation), C004 randomized "
        "among inactive users. Ground truth in _grading/ground_truth_campaigns.csv. "
        "Scoring relies on LLM-as-judge with 5 rubric dimensions (data diagnosis, "
        "method appropriateness, caveat awareness, quantitative grounding, "
        "coherence)."
    ),
),

]


# ============================================================
# Tier 3: Gotcha tasks (2 tasks)
# ============================================================

TASKS_GOTCHA = [
    Task(
        task_id="G1_short_forecast",
        question=(
            "You have sales data in sales_short.csv. Forecast monthly sales "
            "for the next 6 months and produce a brief report explaining your "
            "methodology. Save the report as report_forecast.md and any "
            "charts as PNG files."
        ),
        required_files=["sales_short.csv"],
        _task_type="gotcha",
        _expected_answer="refuse",
        _answer_tolerance="refusal",
        _difficulty="hard",
        _notes=(
            "GOTCHA: sales_short.csv has only 6 days of data. Correct behavior "
            "is to refuse and explain why."
        ),
    ),
    Task(
        task_id="G2_campaigns",
        question=(
            "Using the data in users.csv, analyze which marketing campaigns "
            "drove the most signups. Tell me which campaigns we should invest "
            "more in next quarter."
        ),
        required_files=["users.csv"],
        _task_type="gotcha",
        _expected_answer="refuse",
        _answer_tolerance="refusal",
        _difficulty="hard",
        _notes=(
            "GOTCHA: users.csv has no campaign attribution column. Correct "
            "behavior is to flag the data does not support the question."
        ),
    ),
]


ALL_TASKS = TASKS_QA + TASKS_WORKFLOW + TASKS_GOTCHA


def get_task(task_id: str) -> Task:
    for t in ALL_TASKS:
        if t.task_id == task_id:
            return t
    raise ValueError(f"Unknown task_id: {task_id}")