"""
Generate synthetic datasets for the agent evaluation worked example.

This script creates six CSV files in the data/ directory. Each dataset has
deliberate properties (clean structure, dirty data, planted anomalies, or
insufficient size) chosen to surface specific agent behaviors.

Run once from the project root: python generate_datasets.py
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

# Make results reproducible — these datasets will be identical every time
# this script is run, which matters for reproducibility of the post.
rng = np.random.default_rng(42)

# Ensure the data directory exists
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


# =============================================================
# Dataset 1: sales.csv — clean monthly regional sales data
# =============================================================
# Structure: 12 months x 4 regions x 3 categories = 144 rows.
# Used for: T1 (highest revenue region), T2 (Q4 revenue/unit),
# T3 (H1 vs H2 category growth), W1 (sales report workflow).
#
# Planted properties:
# - West region has highest total revenue (T1 answer = "West")
# - Electronics category has largest H1->H2 growth (T3 answer)
# - Clean, no missing values, well-formed.

months = pd.date_range("2024-01-01", "2024-12-01", freq="MS")
regions = ["North", "South", "East", "West"]
categories = ["Electronics", "Apparel", "Home Goods"]

# Baseline revenue per region (West intentionally highest)
region_baseline = {"North": 80_000, "South": 90_000, "East": 95_000, "West": 120_000}
# Category multipliers (Electronics has growth trend)
category_baseline = {"Electronics": 1.0, "Apparel": 0.7, "Home Goods": 0.5}

sales_rows = []
for month in months:
    for region in regions:
        for category in categories:
            base = region_baseline[region] * category_baseline[category]
            # Add seasonal noise
            seasonal = 1.0 + 0.1 * np.sin(month.month * np.pi / 6)
            # Electronics gets a growth trend in H2
            if category == "Electronics" and month.month >= 7:
                growth = 1.35  # +35% in H2 vs H1
            else:
                growth = 1.0
            noise = rng.normal(1.0, 0.05)
            revenue = base * seasonal * growth * noise
            units_sold = int(revenue / rng.uniform(45, 75))
            sales_rows.append({
                "date": month.strftime("%Y-%m-%d"),
                "region": region,
                "category": category,
                "revenue": round(revenue, 2),
                "units_sold": units_sold,
            })

sales_df = pd.DataFrame(sales_rows)
sales_df.to_csv(DATA_DIR / "sales.csv", index=False)
print(f"Wrote sales.csv ({len(sales_df)} rows)")


# =============================================================
# Dataset 2: users.csv — user analytics with deliberate messiness
# =============================================================
# Structure: 1000 users with id, signup_date, country, plan_tier,
# monthly_spend, is_active.
# Used for: T4 (avg spend active premium), T5 (top country),
# T6 (median 2023 signup spend ex-negatives), W2 (segmentation),
# G2 (gotcha — no campaign column to attribute signups).
#
# Planted properties:
# - 1000 rows total
# - Country values are dirty: "US" / "United States" both appear,
#   "UK" / "United Kingdom" both appear, "CAN" mixed with "Canada",
#   misspelling "I$NDA" mixed with "India" (T5 needs to normalize)
# - ~7% of monthly_spend values are NaN (T4, T6 need to handle)
# - ~3% of monthly_spend values are negative (data entry errors, T6 filters)
# - ~2% of signup_date values are in non-ISO formats (long form,
#   DD/MM/YYYY, M/D/YYYY without zero-padding, "unknown")
# - US is the top country once normalized (T5 answer = "US"/"United States")
# - Very few users from Germany and France — for a gotcha variant
# - No campaign column (G2 should refuse to answer)

n_users = 1000
user_ids = [f"u_{i:04d}" for i in range(n_users)]

# Signup dates spread over 2022-2024
signup_dates = pd.to_datetime(
    rng.integers(
        pd.Timestamp("2022-01-01").value // 10**9,
        pd.Timestamp("2024-12-31").value // 10**9,
        size=n_users,
    ) * 10**9
).normalize()

# Format dates as strings — start with the clean ISO format for all rows
signup_date_strings = signup_dates.strftime("%Y-%m-%d").tolist()

# Inject ~2% problematic date formats. This is realistic — real CSVs
# typically have mixed formats because data comes from multiple systems.
# The agent has to either (a) notice the mixed formats and handle them,
# or (b) silently drop/error on them when parsing.
n_dirty_dates = int(n_users * 0.02)
dirty_date_indices = rng.choice(n_users, size=n_dirty_dates, replace=False)

for idx in dirty_date_indices:
    original_date = signup_dates[idx]
    # Pick one of four realistic dirty formats
    format_choice = rng.integers(0, 4)
    if format_choice == 0:
        # Long form: "January 15, 2023"
        signup_date_strings[idx] = original_date.strftime("%B %d, %Y")
    elif format_choice == 1:
        # European DD/MM/YYYY format (ambiguous when day <= 12!)
        signup_date_strings[idx] = original_date.strftime("%d/%m/%Y")
    elif format_choice == 2:
        # US M/D/YYYY without leading zeros
        signup_date_strings[idx] = f"{original_date.month}/{original_date.day}/{original_date.year}"
    else:
        # Plain garbage — a string that isn't a real date
        signup_date_strings[idx] = "unknown"

# Countries — multiple formats and one misspelling to test normalization.
# Total here is 1010, will be truncated to 1000 after shuffle.
country_choices = (
    ["US"] * 300 + ["United States"] * 300        # both formats for US
    + ["UK"] * 80 + ["United Kingdom"] * 70       # both formats for UK
    + ["Canada"] * 80 + ["CAN"] * 10              # mixed format for Canada
    + ["Australia"] * 80
    + ["India"] * 50 + ["I$NDA"] * 30             # India with deliberate typo
    + ["Germany"] * 20                            # small sample
    + ["France"] * 10                             # very small sample
    + ["Brazil"] * 10
)
rng.shuffle(country_choices)
countries = country_choices[:n_users]

# Plan tiers
plan_tiers = rng.choice(
    ["free", "basic", "premium", "enterprise"],
    size=n_users,
    p=[0.50, 0.30, 0.15, 0.05],
)

# Monthly spend — varies by tier
spend_by_tier = {"free": 0, "basic": 15, "premium": 65, "enterprise": 250}
monthly_spend = np.array([
    max(0, rng.normal(spend_by_tier[tier], spend_by_tier[tier] * 0.2 + 5))
    for tier in plan_tiers
])

# Activity
is_active = rng.choice([True, False], size=n_users, p=[0.7, 0.3])

# Inject ~7% NaN spend values
nan_indices = rng.choice(n_users, size=int(n_users * 0.07), replace=False)
monthly_spend[nan_indices] = np.nan

# Inject ~3% negative spend values (data entry errors)
neg_indices = rng.choice(
    [i for i in range(n_users) if i not in nan_indices],
    size=int(n_users * 0.03),
    replace=False,
)
monthly_spend[neg_indices] = -rng.uniform(10, 100, size=len(neg_indices))

users_df = pd.DataFrame({
    "user_id": user_ids,
    "signup_date": signup_date_strings,
    "country": countries,
    "plan_tier": plan_tiers,
    "monthly_spend": np.round(monthly_spend, 2),
    "is_active": is_active,
})
users_df.to_csv(DATA_DIR / "users.csv", index=False)
print(f"Wrote users.csv ({len(users_df)} rows)")




# =============================================================
# Dataset 3: sensors.csv — hourly sensor data with a planted anomaly
# =============================================================
# Structure: 5 sensors x 30 days x 24 hours = 3600 rows.
# Used for: T7 (avg temp excluding errors), T8 (highest variance sensor),
# W3 (anomaly investigation workflow).
#
# Planted properties:
# - Sensors 1-4 read normally with small noise (~20-25C)
# - Sensor 3 has an anomaly: drifts upward starting day 15, ending
#   ~10C above normal by day 30. (Anomaly investigation answer = sensor_3)
# - Sensor 3 also has the highest variance (T8 answer = sensor_3)
# - ~3% of readings have status="error" and should be excluded (T7)

timestamps = pd.date_range("2024-06-01", periods=24 * 30, freq="h")
sensor_rows = []
for sensor_id in [f"sensor_{i}" for i in range(1, 6)]:
    for ts in timestamps:
        # Base behavior
        if sensor_id == "sensor_3":
            # Planted anomaly: starts drifting day 15
            day_of_period = (ts - timestamps[0]).days
            if day_of_period >= 15:
                drift = (day_of_period - 15) * 0.7  # gradual upward drift
            else:
                drift = 0
            base_temp = 22 + drift
            noise_scale = 0.8  # also slightly noisier
        else:
            base_temp = 22
            noise_scale = 0.3

        temp = rng.normal(base_temp, noise_scale)
        humidity = rng.uniform(40, 60)
        # 3% chance of error status
        status = "error" if rng.random() < 0.03 else "ok"
        sensor_rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_id": sensor_id,
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "status": status,
        })

sensors_df = pd.DataFrame(sensor_rows)
sensors_df.to_csv(DATA_DIR / "sensors.csv", index=False)
print(f"Wrote sensors.csv ({len(sensors_df)} rows)")


# =============================================================
# Dataset 4: customers.csv + orders.csv + order_items.csv
#            — cross-file join data with realistic complexity
# =============================================================
# Used for: T9 (avg Germany order total), T10 (top country by median
# order per customer), W4 (cross-reference report workflow).
#
# Planted complexity:
# - 120 customers (some near-duplicates, some test accounts)
# - 800 orders with multi-currency, statuses, discounts
# - 2400 order_items (avg 3 items per order) — the table that
#   enables double-counting bugs
# - Germany customers have higher order totals AFTER currency conversion
# - Some orders predate the referenced customer's signup_date (data error)
# - A few orphan orders reference non-existent customer_ids
# - A few outlier orders (very large totals)
# - "is_test_account" customers should be filtered out for real analysis

# ---------- customers ----------
n_customers = 120
customer_ids = [f"c_{i:03d}" for i in range(n_customers)]

# Country distribution — but with format inconsistency
raw_countries = rng.choice(
    ["US", "UK", "Germany", "Canada", "Australia"],
    size=n_customers,
    p=[0.40, 0.25, 0.15, 0.12, 0.08],
)

# Add country format messiness: ~10% of country values are in inconsistent form
country_aliases = {
    "Germany": ["DE", "Deutschland"],
    "UK": ["United Kingdom", "GB"],
    "US": ["United States", "USA"],
}
customer_countries = list(raw_countries)
n_country_dirty = int(n_customers * 0.10)
dirty_country_idx = rng.choice(n_customers, size=n_country_dirty, replace=False)
for idx in dirty_country_idx:
    original = customer_countries[idx]
    if original in country_aliases:
        customer_countries[idx] = rng.choice(country_aliases[original])

customer_signup = pd.to_datetime(
    rng.integers(
        pd.Timestamp("2022-01-01").value // 10**9,
        pd.Timestamp("2024-06-30").value // 10**9,
        size=n_customers,
    ) * 10**9
).normalize()

customer_names = [f"Customer_{i}" for i in range(n_customers)]
customer_emails = [f"user{i}@example.com" for i in range(n_customers)]

# Test accounts — ~3% of customers are internal test accounts
is_test_account = np.array([False] * n_customers)
test_idx = rng.choice(n_customers, size=int(n_customers * 0.03), replace=False)
is_test_account[test_idx] = True

# Inject 4 near-duplicate customers (same name + email, different customer_id).
# These represent failed account merges — the same real person appearing twice.
# An agent doing customer-level analysis should ideally dedupe these.
dup_source_idx = rng.choice(
    [i for i in range(n_customers) if i not in test_idx],
    size=4, replace=False
)
dup_target_idx = rng.choice(
    [i for i in range(n_customers) if i not in test_idx and i not in dup_source_idx],
    size=4, replace=False
)
for src, tgt in zip(dup_source_idx, dup_target_idx):
    customer_names[tgt] = customer_names[src]
    customer_emails[tgt] = customer_emails[src]
    customer_countries[tgt] = customer_countries[src]

customers_df = pd.DataFrame({
    "customer_id": customer_ids,
    "name": customer_names,
    "email": customer_emails,
    "signup_date": customer_signup.strftime("%Y-%m-%d"),
    "country": customer_countries,
    "is_test_account": is_test_account,
})
customers_df.to_csv(DATA_DIR / "customers.csv", index=False)
print(f"Wrote customers.csv ({len(customers_df)} rows)")


# ---------- orders ----------
# Country/currency mapping — orders are denominated in local currency.
# An agent that sums "total" without converting will get wrong numbers
# for non-USD customers.
country_currency = {
    "US": "USD", "UK": "GBP", "Germany": "EUR", "DE": "EUR",
    "Deutschland": "EUR", "United Kingdom": "GBP", "GB": "GBP",
    "United States": "USD", "USA": "USD", "Canada": "CAD", "Australia": "AUD",
}
# Conversion rates to USD (approximate, fixed for reproducibility)
to_usd = {"USD": 1.00, "EUR": 1.08, "GBP": 1.27, "CAD": 0.74, "AUD": 0.66}

# Country base order amounts (in local currency).
# Germany is set so that AFTER currency conversion, German orders are highest.
country_avg_order = {
    "US": 120, "United States": 120, "USA": 120,
    "UK": 95, "United Kingdom": 95, "GB": 95,
    "Germany": 320, "DE": 210, "Deutschland": 210,
    "Canada": 130, "Australia": 165,
}

statuses = ["completed", "refunded", "cancelled", "pending"]
status_probs = [0.82, 0.06, 0.07, 0.05]
payment_methods = ["credit_card", "paypal", "wire", "apple_pay"]

n_orders = 800
order_rows = []
for i in range(n_orders):
    # ~2% orphan rate: orders pointing to non-existent customers
    if rng.random() < 0.02:
        customer_id = f"c_{rng.integers(900, 999):03d}"  # not in customers table
        customer_country = "US"  # arbitrary default for currency
    else:
        customer_idx = int(rng.integers(0, n_customers))
        customer_id = customer_ids[customer_idx]
        customer_country = customer_countries[customer_idx]

    currency = country_currency.get(customer_country, "USD")
    avg_local = country_avg_order.get(customer_country, 100)
    total_local = max(10, rng.normal(avg_local, avg_local * 0.3))

    # Inject ~0.5% outliers — huge "B2B contract" orders
    if rng.random() < 0.005:
        total_local = total_local * rng.uniform(50, 200)

    order_date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 365)))

    # ~1.5% of orders predate the customer's signup (data error).
    # Forcing some orders to a date earlier than 2022 for any customer.
    if rng.random() < 0.015:
        order_date = pd.Timestamp("2020-01-01") + pd.Timedelta(days=int(rng.integers(0, 365)))

    status = rng.choice(statuses, p=status_probs)
    discount_pct = round(float(rng.choice([0, 0, 0, 5, 10, 15, 20], p=[0.5, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05])), 1)
    payment_method = rng.choice(payment_methods)

    order_rows.append({
        "order_id": f"o_{i:04d}",
        "customer_id": customer_id,
        "order_date": order_date.strftime("%Y-%m-%d"),
        "total_local": round(total_local, 2),
        "currency": currency,
        "status": status,
        "discount_pct": discount_pct,
        "payment_method": payment_method,
    })

orders_df = pd.DataFrame(order_rows)
orders_df.to_csv(DATA_DIR / "orders.csv", index=False)
print(f"Wrote orders.csv ({len(orders_df)} rows)")


# ---------- order_items ----------
# Each order has 1-5 line items. This is where double-counting bugs happen:
# if the agent joins customers->orders->order_items and groups by country,
# each order's total_local will be counted once per line item.
product_categories = ["Electronics", "Apparel", "Home Goods", "Books", "Beauty"]

order_item_rows = []
item_counter = 0
for _, order in orders_df.iterrows():
    n_items = int(rng.integers(1, 6))  # 1 to 5 items per order
    # Distribute the order total across line items.
    item_weights = rng.uniform(0.5, 1.5, size=n_items)
    item_weights = item_weights / item_weights.sum()
    for j in range(n_items):
        item_total = order["total_local"] * item_weights[j]
        order_item_rows.append({
            "item_id": f"i_{item_counter:05d}",
            "order_id": order["order_id"],
            "product_category": rng.choice(product_categories),
            "quantity": int(rng.integers(1, 4)),
            "item_total_local": round(item_total, 2),
        })
        item_counter += 1

order_items_df = pd.DataFrame(order_item_rows)
order_items_df.to_csv(DATA_DIR / "order_items.csv", index=False)
print(f"Wrote order_items.csv ({len(order_items_df)} rows)")


# =============================================================
# Dataset 6: campaigns.csv + user_events.csv
#            — marketing campaign data for causal analysis (W4)
# =============================================================
# Used for: W4_campaign_analysis (open-ended causal inference task).
#
# Four campaigns with different assignment structures, each requiring
# a different analytical method:
#
# C001: Randomized A/B test, true effect ~15% lift in monthly_spend
# C002: Targeted at high-spend users, apparent effect huge (80%+),
#       true causal effect near zero — selection bias
# C003: Geo-rollout to West region, true effect ~10%, but West was
#       already trending up — parallel trends violation
# C004: Randomized but among inactive users only, true effect 8%
#       reactivation rate, narrow external validity
#
# The agent should diagnose each campaign's assignment type from
# the metadata, recommend the appropriate method, flag caveats.

# ---------- campaigns.csv ----------
campaigns_data = [
    {
        "campaign_id": "C001",
        "name": "Spring Email Blast",
        "channel": "email",
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "assignment_type": "randomized",
        "target_segment": "all_active_users",
        "intended_outcome": "monthly_spend",
        "notes": "Randomly assigned to 50% of eligible users",
    },
    {
        "campaign_id": "C002",
        "name": "Premium Upsell Push",
        "channel": "in_app",
        "start_date": "2024-06-01",
        "end_date": "2024-06-30",
        "assignment_type": "targeted",
        "target_segment": "high_spend_users",
        "intended_outcome": "monthly_spend",
        "notes": "Targeted at users with monthly_spend > $80 in prior period",
    },
    {
        "campaign_id": "C003",
        "name": "West Coast Regional Push",
        "channel": "mixed",
        "start_date": "2024-07-01",
        "end_date": "2024-08-31",
        "assignment_type": "geo_rollout",
        "target_segment": "west_region",
        "intended_outcome": "monthly_spend",
        "notes": "Rolled out to West region only starting July 1",
    },
    {
        "campaign_id": "C004",
        "name": "Win-Back Campaign",
        "channel": "email",
        "start_date": "2024-09-01",
        "end_date": "2024-09-30",
        "assignment_type": "randomized",
        "target_segment": "inactive_users",
        "intended_outcome": "reactivation",
        "notes": "Randomly assigned to 50% of users inactive for 60+ days",
    },
]
campaigns_df = pd.DataFrame(campaigns_data)
campaigns_df.to_csv(DATA_DIR / "campaigns.csv", index=False)
print(f"Wrote campaigns.csv ({len(campaigns_df)} rows)")


# ---------- user_events.csv ----------
# For each campaign, generate exposure records + outcomes for treated and
# control groups. The TRUE causal effects are planted and known.

# We use the user_ids already created above
all_user_ids = users_df["user_id"].tolist()
n_total = len(all_user_ids)

# Synthetic "region" assignment for users — needed for the geo rollout campaign
# Roughly: 30% West, 25% East, 22% South, 23% North
user_regions = rng.choice(
    ["West", "East", "South", "North"],
    size=n_total,
    p=[0.30, 0.25, 0.22, 0.23],
)
user_region_map = dict(zip(all_user_ids, user_regions))

# Use the existing monthly_spend as the "pre-period" baseline (with NaN handled)
pre_spend = users_df.set_index("user_id")["monthly_spend"].to_dict()


def _pre_value(user_id, default=20.0):
    v = pre_spend.get(user_id, default)
    if pd.isna(v) or v < 0:
        return default
    return float(v)


event_rows = []

# -------- C001: Spring Email Blast (randomized, true effect ~15%) --------
# Eligible = all active users. 50% randomized to treatment.
eligible_c001 = users_df[users_df["is_active"] == True]["user_id"].tolist()
treatment_mask = rng.random(len(eligible_c001)) < 0.5
TRUE_EFFECT_C001 = 0.15  # 15% lift

for uid, treated in zip(eligible_c001, treatment_mask):
    pre = _pre_value(uid)
    # Add natural noise + treatment effect if treated
    natural_change = rng.normal(0, 5)
    treatment_lift = pre * TRUE_EFFECT_C001 if treated else 0
    post = max(0, pre + natural_change + treatment_lift)
    event_rows.append({
        "user_id": uid,
        "event_date": "2024-04-15",
        "campaign_id": "C001",
        "exposed": bool(treated),
        "outcome_metric": "monthly_spend",
        "pre_campaign_value": round(pre, 2),
        "post_campaign_value": round(post, 2),
    })

# -------- C002: Premium Upsell Push (targeted, true effect near zero) --------
# Targeted = users with pre-period spend > $80. Apparent "effect" comes from
# the fact that high-spend users continue to spend high; the campaign itself
# does little. True causal lift: 5% (small but present).
TRUE_EFFECT_C002 = 0.05  # 5% real lift

eligible_c002 = [uid for uid in all_user_ids if _pre_value(uid) > 80]
# Also create a "control" group from the same population we COULD have targeted
# but didn't (other high-spend users not in the campaign). In real data this
# control isn't randomized, but for synthesis we include them.
treated_c002 = eligible_c002

# Other high-spenders we'll treat as "control" (but this comparison is biased
# because the treated set was selected based on additional criteria — we
# simulate this by including a wider pool)
not_targeted_high = [uid for uid in all_user_ids
                     if uid not in treated_c002 and _pre_value(uid) > 50]
control_c002 = list(rng.choice(not_targeted_high,
                               size=min(len(treated_c002), len(not_targeted_high)),
                               replace=False))

for uid in treated_c002:
    pre = _pre_value(uid)
    natural_change = rng.normal(0, 5)
    treatment_lift = pre * TRUE_EFFECT_C002
    post = max(0, pre + natural_change + treatment_lift)
    event_rows.append({
        "user_id": uid,
        "event_date": "2024-06-15",
        "campaign_id": "C002",
        "exposed": True,
        "outcome_metric": "monthly_spend",
        "pre_campaign_value": round(pre, 2),
        "post_campaign_value": round(post, 2),
    })

for uid in control_c002:
    pre = _pre_value(uid)
    natural_change = rng.normal(0, 5)
    # Control gets no lift, but their pre-period spend is on average LOWER
    # than the treated group's, so naive comparison will look like treated
    # "outperformed" control purely by selection
    post = max(0, pre + natural_change)
    event_rows.append({
        "user_id": uid,
        "event_date": "2024-06-15",
        "campaign_id": "C002",
        "exposed": False,
        "outcome_metric": "monthly_spend",
        "pre_campaign_value": round(pre, 2),
        "post_campaign_value": round(post, 2),
    })

# -------- C003: West Coast Regional Push (geo, parallel trends violation) --------
# Treated = West region, post-July 2024. True causal effect: 10% lift.
# But the West region was ALREADY trending up before the campaign — we
# simulate this by adding a pre-period upward trend to West users.
TRUE_EFFECT_C003 = 0.10
WEST_PRE_TREND = 0.08  # West was already 8% higher than baseline

for uid in all_user_ids:
    region = user_region_map[uid]
    pre = _pre_value(uid)

    # West region already had higher pre-period values (the parallel trends
    # violation that naive DiD will conflate with causal effect)
    if region == "West":
        pre_adjusted = pre * (1 + WEST_PRE_TREND)
    else:
        pre_adjusted = pre

    natural_change = rng.normal(0, 5)
    # True causal effect only applies to West users post-campaign
    treatment_lift = pre_adjusted * TRUE_EFFECT_C003 if region == "West" else 0
    post = max(0, pre_adjusted + natural_change + treatment_lift)

    event_rows.append({
        "user_id": uid,
        "event_date": "2024-07-15",
        "campaign_id": "C003",
        "exposed": region == "West",
        "outcome_metric": "monthly_spend",
        "pre_campaign_value": round(pre_adjusted, 2),
        "post_campaign_value": round(post, 2),
    })

# -------- C004: Win-Back Campaign (randomized among inactive users) --------
# Eligible = inactive users. Randomized 50/50. Outcome is "reactivation"
# (binary: did they make a purchase in the month after the campaign).
TRUE_EFFECT_C004 = 0.08  # 8 percentage point lift in reactivation rate
BASE_REACTIVATION_RATE = 0.05  # 5% baseline reactivation

inactive_users = users_df[users_df["is_active"] == False]["user_id"].tolist()
treatment_mask_c004 = rng.random(len(inactive_users)) < 0.5

for uid, treated in zip(inactive_users, treatment_mask_c004):
    # Probability of reactivation depends on treatment
    p_reactivate = BASE_REACTIVATION_RATE + (TRUE_EFFECT_C004 if treated else 0)
    reactivated = 1 if rng.random() < p_reactivate else 0
    event_rows.append({
        "user_id": uid,
        "event_date": "2024-09-15",
        "campaign_id": "C004",
        "exposed": bool(treated),
        "outcome_metric": "reactivated",     # binary outcome, not spend
        "pre_campaign_value": 0,              # they were inactive
        "post_campaign_value": reactivated,   # 1 if reactivated, 0 if not
    })


user_events_df = pd.DataFrame(event_rows)
user_events_df.to_csv(DATA_DIR / "user_events.csv", index=False)
print(f"Wrote user_events.csv ({len(user_events_df)} rows)")


# ---------- ground_truth_campaigns.csv (for our reference only — NOT given to agent) ----------
# We record the TRUE effects we planted, so we can later verify whether the
# agent's estimates are close to truth. This file does NOT go in
# task.required_files — the agent never sees it.
ground_truth = pd.DataFrame([
    {
        "campaign_id": "C001",
        "true_effect": TRUE_EFFECT_C001,
        "true_effect_description": "15% lift in monthly_spend (clean A/B test)",
        "expected_method": "t-test or regression on randomized groups",
    },
    {
        "campaign_id": "C002",
        "true_effect": TRUE_EFFECT_C002,
        "true_effect_description": "5% lift (most apparent effect is selection bias)",
        "expected_method": "matching/IPW, or note untestable observationally",
    },
    {
        "campaign_id": "C003",
        "true_effect": TRUE_EFFECT_C003,
        "true_effect_description": "10% lift, but West was already trending up (parallel trends violation)",
        "expected_method": "difference-in-differences with parallel trends check",
    },
    {
        "campaign_id": "C004",
        "true_effect": TRUE_EFFECT_C004,
        "true_effect_description": "8 percentage point lift in reactivation rate (randomized among inactive)",
        "expected_method": "t-test on reactivation rates, note narrow population",
    },
])

GRADING_DIR = Path("_grading")
GRADING_DIR.mkdir(exist_ok=True)
ground_truth.to_csv(GRADING_DIR / "ground_truth_campaigns.csv", index=False)
print(f"Wrote _grading/ground_truth_campaigns.csv ({len(ground_truth)} rows) "
      f"(for grading only — not exposed to agent)")



# =============================================================
# Summary
# =============================================================
print("\nAll datasets generated successfully.")
print(f"Files in {DATA_DIR.absolute()}:")
for f in sorted(DATA_DIR.glob("*.csv")):
    print(f"  {f.name}")