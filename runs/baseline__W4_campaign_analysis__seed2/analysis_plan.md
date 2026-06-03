# Marketing Campaign Causal Impact Analysis Plan

**Prepared for:** Marketing Director  
**Date:** 2024  
**Objective:** Measure the causal impact of Q2-Q3 2024 marketing campaigns and provide investment recommendations for next quarter

---

## Executive Summary

We analyzed four marketing campaigns conducted between April and September 2024. Our analysis reveals:

- **C001 (Spring Email Blast)**: Moderate positive effect (+$4.41), but not statistically significant (p=0.346)
- **C002 (Premium Upsell Push)**: Strong positive effect (+$9.76), statistically significant (p<0.001) ✓
- **C003 (West Coast Regional Push)**: Moderate positive effect (+$3.11), not statistically significant (p=0.111)
- **C004 (Win-Back Campaign)**: Strong positive effect on reactivation (+10.8 percentage points), statistically significant (p=0.005) ✓

**Key Recommendation:** Invest heavily in C002 (Premium Upsell) and C004 (Win-Back) campaigns. Consider refinements to C001 and C003 before scaling.

---

## Campaign 1: Spring Email Blast (C001)

### Data Characteristics
- **Type:** Experimental (Randomized A/B Test)
- **Period:** April 1-30, 2024
- **Sample Size:** 710 users (359 exposed, 351 control)
- **Target:** All active users
- **Assignment:** Random assignment to 50% of eligible users
- **Outcome:** Monthly spend

### Analytical Method: Standard A/B Test Analysis

**Why this method?**  
Random assignment creates comparable treatment and control groups, allowing us to directly attribute differences in outcomes to the campaign. This is the gold standard for causal inference.

**Pre-Campaign Balance Check:**
- Exposed group: $28.11
- Control group: $28.14
- Difference: -$0.03 ✓ (Groups are well-balanced)

**Results:**
- **Average Treatment Effect (ATE):** +$4.41 per user
- **Lift:** 15.5% increase in monthly spend
- **Statistical Significance:** p = 0.346 (NOT significant at α=0.05)
- **95% Confidence Interval:** Approximately [-$4.80, +$13.62]

### Interpretation & Caveats

**What we can conclude:**
- The campaign shows a positive directional effect, but we cannot rule out that this is due to random chance
- The effect size (15.5% lift) is economically meaningful if real

**Limitations:**
1. **Insufficient statistical power:** With 710 users, we may not have enough sample size to detect a moderate effect
2. **High variance:** Monthly spend has high variability, making it harder to detect effects
3. **Timing:** April may have seasonal factors affecting spend

**Recommendation:** MODERATE CONFIDENCE
- The campaign shows promise but needs validation
- Consider running a larger follow-up test (1,500+ users) to achieve 80% power
- Alternatively, test variations of the email content/timing to improve effect size

---

## Campaign 2: Premium Upsell Push (C002)

### Data Characteristics
- **Type:** Observational (Targeted Campaign)
- **Period:** June 1-30, 2024
- **Sample Size:** 144 users (72 exposed, 72 control)
- **Target:** High-spend users (monthly_spend > $80 in prior period)
- **Assignment:** Targeted (non-random)
- **Outcome:** Monthly spend

### Analytical Method: Difference-in-Differences (DiD)

**Why this method?**  
This campaign was targeted at high-spenders, creating selection bias. Simple comparison would be misleading because exposed users already spend more. DiD controls for pre-existing differences by comparing the *change* in outcomes.

**Pre-Campaign Balance Check:**
- Exposed group: $200.35
- Control group: $64.77
- Difference: +$135.59 ⚠️ (Groups are NOT balanced - expected for targeted campaign)

**Naive Comparison (MISLEADING):**
- Post-campaign difference: +$145.35
- This overstates the effect because exposed users were already higher spenders

**Difference-in-Differences Analysis:**
- Exposed group change: +$9.72
- Control group change: -$0.04
- **DiD Estimate:** +$9.76 per user
- **Statistical Significance:** p < 0.001 ✓✓✓

### Interpretation & Caveats

**What we can conclude:**
- The campaign caused a statistically significant increase in spending among high-value users
- The effect is robust and unlikely due to chance
- High-spenders increased spend by ~$10/month more than they would have without the campaign

**Limitations:**
1. **Parallel trends assumption:** DiD assumes both groups would have followed similar trends without treatment. We cannot fully verify this with only pre/post data
2. **Small sample size:** Only 144 users, though the effect is strong enough to be significant
3. **Regression to the mean:** High spenders might naturally fluctuate; some of the control group decline could be regression to mean
4. **Selection on unobservables:** If exposed users differ in ways we can't measure (e.g., engagement level), estimates may be biased

**Recommendation:** HIGH CONFIDENCE
- This campaign shows strong, statistically significant results
- **Action:** Scale this campaign to all high-spend users (monthly_spend > $80)
- **Expected ROI:** If campaign cost < $9.76 per user per month, this is profitable
- **Monitor:** Track whether effects persist over multiple months

---

## Campaign 3: West Coast Regional Push (C003)

### Data Characteristics
- **Type:** Quasi-Experimental (Geographic Rollout)
- **Period:** July 1 - August 31, 2024
- **Sample Size:** 1,000 users (274 West Coast, 726 Other regions)
- **Target:** West region users
- **Assignment:** Geographic (all West Coast users exposed)
- **Outcome:** Monthly spend

### Analytical Method: Difference-in-Differences with Geographic Controls

**Why this method?**  
Geographic rollouts create natural experiments. We compare the West Coast (treated) to other regions (control), using DiD to account for pre-existing regional differences.

**Pre-Campaign Balance Check:**
- West Coast: $31.47
- Other regions: $27.70
- Difference: +$3.77 (West Coast users spend slightly more at baseline)

**Difference-in-Differences Analysis:**
- West Coast change: +$3.76
- Other regions change: +$0.64
- **DiD Estimate:** +$3.11 per user
- **Statistical Significance:** p = 0.111 (NOT significant at α=0.05)

### Interpretation & Caveats

**What we can conclude:**
- The campaign shows a positive directional effect (+$3.11)
- However, we cannot confidently rule out that this is due to chance or regional trends
- The effect is smaller than C001 and C002

**Limitations:**
1. **Geographic confounding:** Regional differences in seasonality, economy, or other factors could bias results
2. **Parallel trends assumption:** We assume other regions are a valid counterfactual for West Coast trends
3. **Spillover effects:** If the campaign used national channels (e.g., social media), control regions may have been partially exposed
4. **Limited pre-period data:** We only have one pre-period measurement, making trend validation difficult
5. **Unequal group sizes:** 274 vs 726 users creates asymmetric precision

**Recommendation:** MODERATE CONFIDENCE
- The campaign shows promise but lacks statistical significance
- **Before scaling:**
  - Conduct a randomized test within the West Coast region (50% exposed, 50% control)
  - Collect more pre-period data to validate parallel trends
  - Investigate whether the effect varies by sub-region or user characteristics
- **Alternative:** Test in another region (e.g., East Coast) to see if effects replicate

---

## Campaign 4: Win-Back Campaign (C004)

### Data Characteristics
- **Type:** Experimental (Randomized A/B Test)
- **Period:** September 1-30, 2024
- **Sample Size:** 290 users (147 exposed, 143 control)
- **Target:** Inactive users (60+ days without activity)
- **Assignment:** Random assignment to 50% of eligible users
- **Outcome:** Reactivation (binary) and post-campaign spend

### Analytical Method: Standard A/B Test with Binary Outcome

**Why this method?**  
Random assignment ensures causal validity. For reactivation (binary outcome), we use proportion tests. For spend, we use standard t-tests.

**Pre-Campaign Balance Check:**
- Exposed group: $0.00
- Control group: $0.00
- Difference: $0.00 ✓ (Perfect balance - all users were inactive)

**Reactivation Results:**
- **Exposed reactivation rate:** 15.6% (23/147 users)
- **Control reactivation rate:** 4.9% (7/143 users)
- **Reactivation Lift:** +10.8 percentage points
- **Statistical Significance:** p = 0.005 ✓✓ (Chi-square test)

**Spend Results:**
- **Average Treatment Effect:** +$0.11 per user
- **Statistical Significance:** p = 0.003 ✓✓

### Interpretation & Caveats

**What we can conclude:**
- The campaign successfully reactivated inactive users at 3x the natural reactivation rate
- This is a strong, statistically significant effect
- Even small amounts of reactivated spend can be valuable for long-term retention

**Limitations:**
1. **Short-term measurement:** We only observe one month post-campaign. Reactivated users may churn again
2. **Low absolute spend:** Reactivated users spend little ($0.11 average), though this is expected for previously inactive users
3. **Sample size:** 290 users is adequate for detecting the observed effect, but limits subgroup analysis
4. **Definition of reactivation:** We define it as any spend > $0, but different thresholds might show different results

**Recommendation:** HIGH CONFIDENCE
- This campaign is highly effective at reactivating dormant users
- **Action:** Make this a recurring monthly campaign for all users inactive 60+ days
- **Optimization opportunities:**
  - Test different messaging/offers to increase reactivation rate further
  - Implement a follow-up nurture sequence for reactivated users to prevent re-churn
  - Track 3-month and 6-month retention of reactivated users
- **Expected value:** If customer lifetime value of reactivated users > campaign cost, this is profitable

---

## Comparative Analysis & Investment Recommendations

### Summary Table

| Campaign | Method | Effect Size | P-Value | Significance | Recommendation |
|----------|--------|-------------|---------|--------------|----------------|
| C001: Spring Email | A/B Test | +$4.41 | 0.346 | ✗ | Moderate - Refine & Retest |
| C002: Premium Upsell | DiD | +$9.76 | <0.001 | ✓✓✓ | High - Scale Immediately |
| C003: West Coast | DiD | +$3.11 | 0.111 | ✗ | Moderate - Validate First |
| C004: Win-Back | A/B Test | +10.8pp | 0.005 | ✓✓ | High - Implement Recurring |

### Investment Priorities for Next Quarter

**Tier 1 - High Confidence, Scale Immediately:**

1. **Premium Upsell Push (C002)**
   - Expand to all users with monthly_spend > $80
   - Expected incremental revenue: $9.76 × number of high-spenders per month
   - Monitor for diminishing returns or fatigue effects

2. **Win-Back Campaign (C004)**
   - Implement as recurring monthly campaign
   - Target all users inactive 60+ days
   - Expected reactivation: ~11% lift in reactivation rate
   - Add retention tracking to measure long-term value

**Tier 2 - Moderate Confidence, Optimize Before Scaling:**

3. **Spring Email Blast (C001)**
   - Run optimization tests on:
     - Email subject lines and content
     - Send timing (day of week, time of day)
     - Audience segmentation
   - Increase sample size to 1,500+ users for better statistical power
   - Only scale if optimized version shows p < 0.05

4. **West Coast Regional Push (C003)**
   - Validate with randomized test within region
   - Test in additional geographic markets
   - Investigate whether effect varies by user segment
   - Consider whether "mixed channel" approach needs refinement

### Budget Allocation Recommendation

If you have $100K to allocate next quarter:
- **50% ($50K)** → Premium Upsell (C002) - Proven ROI
- **30% ($30K)** → Win-Back Campaign (C004) - High reactivation value
- **15% ($15K)** → Spring Email optimization tests (C001)
- **5% ($5K)** → West Coast validation study (C003)

---

## Methodological Notes for Stakeholders

### Why Different Methods for Different Campaigns?

The choice of analytical method depends on how users were assigned to campaigns:

- **Randomized A/B Tests (C001, C004):** When assignment is random, we can directly compare outcomes. This is the gold standard.

- **Difference-in-Differences (C002, C003):** When assignment is non-random (targeted or geographic), we must account for pre-existing differences. DiD does this by comparing changes over time.

### Understanding Statistical Significance

- **p < 0.05:** Less than 5% chance the result is due to random variation (conventional threshold)
- **p < 0.01:** Less than 1% chance (strong evidence)
- **p > 0.05:** Cannot rule out random chance (doesn't mean "no effect," just "not proven")

### Key Assumptions & Limitations

All causal inference methods require assumptions:

1. **A/B Tests assume:** No interference between users, stable treatment, proper randomization
2. **DiD assumes:** Parallel trends (control group shows what would have happened to treatment group)
3. **All methods assume:** Accurate measurement, no data quality issues, representative samples

---

## Next Steps & Ongoing Monitoring

### Immediate Actions (This Quarter)
1. Scale C002 and C004 campaigns
2. Set up automated reporting dashboards for ongoing monitoring
3. Design optimization tests for C001
4. Plan validation study for C003

### Ongoing Monitoring (Monthly)
- Track campaign effects over time to detect decay or fatigue
- Monitor for spillover effects or cannibalization between campaigns
- Conduct quarterly meta-analysis to update effect estimates
- Test new campaign variations using A/B testing framework

### Long-Term Learning (Quarterly)
- Build predictive models to identify which users respond best to each campaign
- Develop personalization strategies based on user characteristics
- Measure customer lifetime value impact, not just immediate spend
- Create a campaign testing roadmap for continuous optimization

---

## Appendix: Technical Details

### Statistical Tests Used
- **Two-sample t-tests:** For continuous outcomes (monthly spend)
- **Chi-square tests:** For binary outcomes (reactivation)
- **Difference-in-differences:** For non-randomized assignments

### Sample Size Calculations
For future campaigns, to detect a $5 effect with 80% power:
- Required sample size: ~1,250 users per group (2,500 total)
- For 10% reactivation lift: ~400 users per group (800 total)

### Data Quality Notes
- Pre-campaign values well-measured for all campaigns
- No missing data issues detected
- Outcome measurement period consistent across campaigns

---

**Questions or need additional analysis?** Contact the analytics team for deep-dives on specific campaigns or custom analyses.
