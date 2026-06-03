# Marketing Campaign Causal Impact Analysis Plan

## Executive Summary

This analysis evaluates the causal impact of four marketing campaigns conducted in 2024. Two campaigns (C001 and C004) used randomized controlled trials and provide **high-confidence causal estimates**. Two campaigns (C002 and C003) used observational designs and require additional validation before scaling.

### Key Recommendations:
- **SCALE UP**: C001 (Spring Email Blast) and C004 (Win-Back Campaign) - Strong causal evidence
- **VALIDATE FIRST**: C002 (Premium Upsell) and C003 (West Coast Regional) - Promising but need confirmation

---

## Campaign C001: Spring Email Blast

### 1. Data Type & Design
**Experimental - Randomized Controlled Trial (RCT)**

- **Assignment**: Random assignment to 50% of all active users
- **Sample Size**: 710 users (359 exposed, 351 control)
- **Period**: April 1-30, 2024
- **Outcome**: Monthly spend ($)

### 2. Analytical Method
**Standard A/B Test Analysis**

This is the gold standard for causal inference. Random assignment ensures that exposed and control groups are statistically equivalent at baseline, allowing us to attribute any differences in outcomes directly to the campaign.

**Analysis Approach:**
- Compare average lift (post - pre) between exposed and control groups
- Use two-sample t-test for statistical significance
- Calculate confidence intervals for effect size

### 3. Results

| Metric | Exposed Group | Control Group | Difference |
|--------|---------------|---------------|------------|
| Pre-campaign spend | $28.11 | $28.14 | -$0.03 |
| Post-campaign spend | $32.86 | $28.45 | +$4.41 |
| Average lift | **$4.75** | **$0.31** | **$4.44** |

**Statistical Significance:**
- Average Treatment Effect (ATE): **$4.44 per user**
- 95% Confidence Interval: [$3.37, $5.52]
- P-value: < 0.0001 (highly significant)
- Balance check: Groups well-balanced at baseline (p = 0.994)

### 4. Caveats & Limitations

✓ **Strengths:**
- Proper randomization confirmed by balance check
- Large sample size provides good statistical power
- Clean causal interpretation

⚠ **Limitations:**
- Results apply to active users only (not generalizable to inactive users)
- Short-term effect (1 month) - long-term impact unknown
- Doesn't account for potential spillover effects between users
- Email channel saturation effects not measured

### 5. Recommendation
**SCALE UP** - This campaign has strong causal evidence of a $4.44 increase in monthly spend per user. With proper cost-benefit analysis, this is a strong candidate for expansion.

---

## Campaign C002: Premium Upsell Push

### 1. Data Type & Design
**Observational - Targeted Assignment (Non-Randomized)**

- **Assignment**: Targeted at high-spending users (monthly_spend > $80)
- **Sample Size**: 144 users (72 exposed, 72 control)
- **Period**: June 1-30, 2024
- **Outcome**: Monthly spend ($)

### 2. Analytical Method
**Difference-in-Differences (DiD) with Caution**

Since this campaign targeted high spenders, the exposed and control groups are fundamentally different. A naive comparison would suffer from severe selection bias.

**Analysis Approach:**
- Use DiD to control for baseline differences in spending levels
- Compare change in spending (post - pre) between groups
- **Critical assumption**: Parallel trends (both groups would have changed similarly without treatment)

### 3. Results

| Metric | Exposed Group | Control Group | Difference |
|--------|---------------|---------------|------------|
| Pre-campaign spend | **$200.35** | **$64.77** | +$135.58 ⚠ |
| Post-campaign spend | $210.07 | $64.73 | +$145.34 |
| Average lift | **$9.72** | **-$0.04** | **$9.76** |

**Statistical Analysis:**
- DiD Estimate: **$9.76 per user**
- 95% Confidence Interval: [$7.72, $11.80]
- P-value: < 0.0001
- **Balance check: FAILED** (p < 0.0001) - Groups highly imbalanced at baseline

### 4. Caveats & Limitations

⚠ **Critical Issues:**
- **Selection bias**: Exposed group had 3x higher baseline spending
- **Parallel trends assumption**: Likely violated - high spenders may have different natural growth trajectories
- **Regression to the mean**: High spenders selected based on prior period may naturally decrease
- **Confounding**: Other factors correlated with high spending may drive results

⚠ **What the $9.76 estimate means:**
- This is the difference in spending changes between groups
- It controls for baseline level differences
- BUT it assumes both groups would have changed similarly without treatment
- This assumption is questionable given the targeted selection

### 5. Recommendation
**VALIDATE BEFORE SCALING** - While the effect appears large and significant, the non-randomized design creates substantial uncertainty about causality. 

**Next Steps:**
1. Run a proper randomized A/B test on high-spending users
2. Analyze historical trends to assess parallel trends assumption
3. Consider propensity score matching to find better control group
4. Test on a small randomized sample before full rollout

---

## Campaign C003: West Coast Regional Push

### 1. Data Type & Design
**Quasi-Experimental - Geographic Rollout**

- **Assignment**: All users in West region received campaign; other regions did not
- **Sample Size**: 1,000 users (274 West, 726 Other regions)
- **Period**: July 1 - August 31, 2024
- **Outcome**: Monthly spend ($)

### 2. Analytical Method
**Difference-in-Differences (DiD)**

Geographic rollouts are common in marketing but create challenges for causal inference. We can't randomize geography, so we must compare regions and assume they would have trended similarly without the campaign.

**Analysis Approach:**
- Compare West region (treated) to other regions (control)
- Use DiD to account for baseline regional differences
- **Critical assumption**: Parallel trends across regions

### 3. Results

| Metric | West Region | Other Regions | Difference |
|--------|-------------|---------------|------------|
| Pre-campaign spend | $31.47 | $27.70 | +$3.77 |
| Post-campaign spend | $35.23 | $28.35 | +$6.88 |
| Average lift | **$3.76** | **$0.64** | **$3.11** |

**Statistical Analysis:**
- DiD Estimate: **$3.11 per user**
- 95% Confidence Interval: [$2.14, $4.09]
- P-value: < 0.0001
- Balance check: Groups reasonably balanced at baseline (p = 0.368)

### 4. Caveats & Limitations

⚠ **Threats to Validity:**
- **Regional confounds**: Other factors may differ between West and other regions
  - Economic conditions (e.g., tech sector concentration on West Coast)
  - Seasonal patterns (e.g., summer vacation behavior)
  - Competitive activity in specific regions
  - Other marketing activities not captured in data
- **Parallel trends assumption**: Cannot verify without pre-campaign time series
- **Spillover effects**: Users may travel between regions
- **SUTVA violation**: West Coast users may influence other users through network effects

⚠ **What the $3.11 estimate means:**
- This is the difference in spending changes between regions
- It assumes regions would have trended similarly without the campaign
- Regional economic or seasonal factors could explain some or all of this difference

### 5. Recommendation
**VALIDATE BEFORE SCALING** - The effect is statistically significant and groups appear balanced, but geographic confounding is a serious concern.

**Next Steps:**
1. Analyze pre-campaign trends to assess parallel trends assumption
2. Check for concurrent regional events or campaigns during July-August
3. Consider a randomized rollout within regions (e.g., random zip codes)
4. Implement a staggered rollout design for better causal identification
5. If scaling, monitor closely for regional heterogeneity

---

## Campaign C004: Win-Back Campaign

### 1. Data Type & Design
**Experimental - Randomized Controlled Trial (RCT)**

- **Assignment**: Random assignment to 50% of inactive users (60+ days)
- **Sample Size**: 290 users (147 exposed, 143 control)
- **Period**: September 1-30, 2024
- **Outcome**: Reactivation (binary)

### 2. Analytical Method
**Standard A/B Test Analysis for Binary Outcomes**

This is a well-designed randomized experiment with a binary outcome (reactivated vs. not reactivated).

**Analysis Approach:**
- Compare reactivation rates between exposed and control groups
- Use chi-square test or proportion test for statistical significance
- Calculate absolute risk difference (percentage point increase)

### 3. Results

| Metric | Exposed Group | Control Group | Difference |
|--------|---------------|---------------|------------|
| Sample size | 147 | 143 | - |
| Reactivated | 23 users | 7 users | - |
| Reactivation rate | **15.6%** | **4.9%** | **+10.8 pp** |

**Statistical Analysis:**
- Average Treatment Effect: **+10.8 percentage points**
- 95% Confidence Interval: [+3.9 pp, +17.6 pp]
- Chi-square p-value: 0.0049 (significant)
- Relative increase: 3.2x higher reactivation rate

### 4. Caveats & Limitations

✓ **Strengths:**
- Proper randomization
- Clear binary outcome
- Statistically significant result
- Addresses important business problem (churn)

⚠ **Limitations:**
- Smaller sample size than C001 (wider confidence intervals)
- Only measures immediate reactivation (1 month)
- Doesn't measure quality of reactivation (spending level, retention)
- May have diminishing returns if repeated frequently
- Inactive users may differ from those who churned permanently

⚠ **Additional Considerations:**
- What happens to reactivated users in months 2-6?
- Do reactivated users spend at previous levels?
- Is there a fatigue effect from repeated win-back attempts?

### 5. Recommendation
**SCALE UP WITH MONITORING** - Strong causal evidence of 10.8 percentage point increase in reactivation. This is a 3x improvement over natural reactivation rate.

**Next Steps:**
1. Track long-term retention of reactivated users
2. Measure lifetime value of reactivated users vs. cost
3. Test frequency caps to avoid fatigue
4. Segment by inactivity duration to optimize targeting

---

## Overall Investment Recommendations

### Tier 1: Ready to Scale (High Confidence)
1. **C004: Win-Back Campaign** - 10.8 pp reactivation lift, strong RCT evidence
2. **C001: Spring Email Blast** - $4.44 spending lift, strong RCT evidence

### Tier 2: Validate Before Scaling (Medium Confidence)
3. **C002: Premium Upsell Push** - $9.76 apparent lift, but selection bias concerns
4. **C003: West Coast Regional** - $3.11 apparent lift, but geographic confounding concerns

### Investment Strategy

**Immediate Actions:**
- **Scale C001 and C004**: These have strong causal evidence and can be expanded confidently
- **Run validation tests for C002 and C003**: Design proper randomized experiments

**For C002 (Premium Upsell):**
- Randomly assign 50% of high-spending users to receive the upsell push
- This will provide clean causal estimate without selection bias
- Estimated sample needed: 200+ users for 80% power

**For C003 (West Coast Regional):**
- Implement staggered geographic rollout or randomized zip code assignment
- Collect pre-campaign time series to validate parallel trends
- Consider synthetic control methods if randomization not feasible

---

## Methodological Appendix

### Why Randomization Matters

**Randomized experiments (C001, C004):**
- Create statistically equivalent groups
- Eliminate selection bias
- Allow direct causal interpretation
- Gold standard for decision-making

**Observational studies (C002, C003):**
- Groups may differ in unobserved ways
- Require strong assumptions (parallel trends)
- More vulnerable to confounding
- Need additional validation

### Key Assumptions by Method

**A/B Test (C001, C004):**
- ✓ Random assignment
- ✓ No interference between units (SUTVA)
- ✓ Stable treatment effect

**Difference-in-Differences (C002, C003):**
- ⚠ Parallel trends (untestable without pre-period data)
- ⚠ No time-varying confounders
- ⚠ Stable composition of groups

### Statistical Significance vs. Practical Significance

All four campaigns show statistically significant effects (p < 0.05), but this doesn't mean all should be scaled:

- **Statistical significance** = Effect is unlikely due to chance
- **Practical significance** = Effect is large enough to matter for business
- **Causal validity** = Effect is truly caused by campaign, not confounding

C001 and C004 have all three. C002 and C003 have statistical significance but questionable causal validity.

---

## Conclusion

The marketing team has run a mix of experimental and observational campaigns. The randomized experiments (C001 and C004) provide strong evidence for scaling. The observational campaigns (C002 and C003) show promising results but require validation through proper randomized testing before major investment.

**Key Principle**: When making investment decisions, prioritize causal validity over statistical significance. A smaller but certain effect is more valuable than a larger but uncertain one.

---

*Analysis conducted using difference-in-differences, A/B testing, and causal inference methods. All statistical tests use α = 0.05 significance level.*
