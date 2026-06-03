# Marketing Campaign Causal Impact Analysis Plan

**Prepared for:** Marketing Director  
**Date:** Analysis of Q2-Q4 2024 Campaigns  
**Objective:** Measure causal impact of marketing campaigns to inform Q1 2025 investment decisions

---

## Executive Summary

We analyzed four marketing campaigns run in 2024 using appropriate causal inference methods matched to each campaign's design. **Key findings:**

| Campaign | Method | Effect | Confidence | Recommendation |
|----------|--------|--------|------------|----------------|
| **C001: Spring Email Blast** | A/B Test | **+$4.44/user** | ★★★ High | **SCALE UP** - Strong ROI |
| **C002: Premium Upsell** | Regression | **+$2.87/user** | ★★☆ Medium | Continue with caution |
| **C003: West Coast Regional** | Diff-in-Diff | **+$3.11/user** | ★★★ High | **EXPAND** to other regions |
| **C004: Win-Back Campaign** | A/B Test | **+$0.11/user** | ★★☆ Medium | Optimize or reconsider |

**Bottom Line:** C001 and C003 show the strongest evidence of positive impact and should be prioritized for Q1 2025 investment.

---

## Campaign C001: Spring Email Blast

### 1. Data Type & Design
- **Type:** Randomized Controlled Trial (A/B Test)
- **Assignment:** Random assignment to 50% of active users
- **Sample Size:** 710 users (359 treatment, 351 control)
- **Period:** April 2024
- **Outcome:** Monthly spending

### 2. Analytical Method: A/B Test Analysis

**Why this method?**  
Random assignment creates comparable treatment and control groups, allowing us to directly measure the causal effect without confounding.

**Analysis:**
- **Treatment group change:** +$4.75 (from $28.11 to $32.86)
- **Control group change:** +$0.31 (from $28.14 to $28.45)
- **Average Treatment Effect (ATE):** **$4.44 per user**
- **95% Confidence Interval:** [$3.37, $5.52]
- **Statistical Significance:** p < 0.001 (highly significant)

**Balance Check:** ✓ PASSED  
Pre-campaign spending was nearly identical between groups ($28.11 vs $28.14, p=0.99), confirming successful randomization.

### 3. Caveats & Limitations
- ✓ **Minimal concerns** - This is the gold standard design
- Campaign ran in April; seasonal effects may differ in other months
- Effect measured over one month; long-term retention effects unknown
- Sample limited to "active users" - may not generalize to inactive users

### 4. Recommendation
**STRONG INVEST** - This campaign has the highest confidence causal estimate. The effect is large ($4.44), statistically robust, and the randomized design eliminates selection bias concerns.

**Estimated ROI:** ~4,340% (assuming $0.10 email cost per user)

---

## Campaign C002: Premium Upsell Push

### 1. Data Type & Design
- **Type:** Observational (Targeted Campaign)
- **Assignment:** Targeted at high-spending users (monthly_spend > $80)
- **Sample Size:** 144 users (72 treatment, 72 control)
- **Period:** June 2024
- **Outcome:** Monthly spending

### 2. Analytical Method: Regression with Controls

**Why this method?**  
The campaign was **not randomized** - it specifically targeted high spenders. This creates **selection bias**: treatment and control groups differ systematically.

**Evidence of Selection Bias:**
- Treatment group pre-campaign average: **$200.35**
- Control group pre-campaign average: **$64.77**
- Difference: $135.58 (p < 0.001) - groups are NOT comparable

**Analysis:**

| Approach | Estimate | Issue |
|----------|----------|-------|
| Naive comparison | +$9.76 | **BIASED** - confounded by baseline differences |
| Regression-adjusted | **+$2.87** | Controls for pre-campaign spending |

**Regression Results:**
- **Adjusted Treatment Effect:** **$2.87 per user**
- **Standard Error:** $1.22
- **P-value:** 0.020 (significant at 5% level)
- **Model R²:** 0.574 (explains 57% of variance)

The regression model controls for pre-campaign spending, which accounts for much of the selection bias. The adjusted effect is **70% smaller** than the naive estimate.

### 3. Caveats & Limitations
⚠️ **MODERATE CONCERNS**

1. **Residual Confounding:** Even after controlling for pre-campaign spending, other unmeasured factors may differ between high and low spenders (e.g., engagement, product usage, demographics)

2. **Regression Assumptions:** The linear relationship assumption may not fully capture complex spending patterns

3. **Limited Sample Size:** Only 144 users reduces statistical power

4. **Ceiling Effects:** High spenders may have less room to increase spending

### 4. Recommendation
**PROCEED WITH CAUTION** - The effect is positive and statistically significant, but the observational design limits our confidence in the causal interpretation.

**Next Steps:**
- Run a **randomized A/B test** within the high-spender segment to get a clean causal estimate
- Consider testing on medium spenders ($40-$80) to find optimal targeting threshold
- Track long-term retention and lifetime value, not just immediate spending

**Estimated ROI:** ~474% (assuming $0.50 in-app cost per user, but with uncertainty)

---

## Campaign C003: West Coast Regional Push

### 1. Data Type & Design
- **Type:** Quasi-Experimental (Geographic Rollout)
- **Assignment:** All users in West region received treatment; other regions as control
- **Sample Size:** 1,000 users (274 West, 726 Other)
- **Period:** July-August 2024
- **Outcome:** Monthly spending

### 2. Analytical Method: Difference-in-Differences (DiD)

**Why this method?**  
Geographic rollouts are not randomized - West Coast users may differ from other regions. DiD controls for **time-invariant regional differences** by comparing the *change* in outcomes.

**DiD Logic:**
- If West Coast users naturally spend more, that's captured in pre-campaign levels
- We measure whether the *change* in West Coast spending exceeds the *change* in other regions
- This differences out regional baseline differences

**Analysis:**

| Region | Pre-Campaign | Post-Campaign | Change |
|--------|--------------|---------------|--------|
| West Coast (Treatment) | $31.47 | $35.23 | **+$3.76** |
| Other Regions (Control) | $27.70 | $28.35 | **+$0.64** |

**Difference-in-Differences Estimate:** **$3.11 per user**
- **95% Confidence Interval:** [$2.14, $4.09]
- **Statistical Significance:** p < 0.001 (highly significant)

**Parallel Trends Check:** ✓ PASSED  
Pre-campaign spending levels differed by $3.77 (expected for different regions), but this difference was not statistically significant (p=0.37), supporting the parallel trends assumption.

### 3. Caveats & Limitations
⚠️ **MINOR CONCERNS**

1. **Parallel Trends Assumption:** We can only test this indirectly. If West Coast and other regions were on different spending trajectories before the campaign, DiD could be biased.

2. **Spillover Effects:** If the campaign affected other regions (e.g., through social media), the control group is contaminated.

3. **Regional Heterogeneity:** The effect may be specific to West Coast characteristics (demographics, competition, etc.)

4. **Time-Varying Confounders:** Other events in July-August that affected regions differently could bias results

### 4. Recommendation
**STRONG INVEST & EXPAND** - The DiD design provides credible causal evidence. The effect is substantial ($3.11) and statistically robust.

**Next Steps:**
- **Roll out to other regions** (East Coast, Midwest) to test generalizability
- Monitor for diminishing returns as campaign scales
- Consider running a randomized test within a region to validate the DiD estimate

**Estimated ROI:** ~937% (assuming $0.30 mixed channel cost per user)

---

## Campaign C004: Win-Back Campaign

### 1. Data Type & Design
- **Type:** Randomized Controlled Trial (A/B Test)
- **Assignment:** Random assignment to 50% of inactive users (60+ days)
- **Sample Size:** 290 users (147 treatment, 143 control)
- **Period:** September 2024
- **Outcome:** Reactivation & spending

### 2. Analytical Method: A/B Test Analysis

**Why this method?**  
Random assignment among inactive users creates comparable groups for causal inference.

**Analysis - Reactivation (Primary Outcome):**
- **Treatment reactivation rate:** 15.6% (23 of 147 users)
- **Control reactivation rate:** 4.9% (7 of 143 users)
- **Lift:** **+10.8 percentage points**
- **Statistical Significance:** p = 0.005 (significant)

**Analysis - Spending (Secondary Outcome):**
- **Treatment group change:** +$0.16 (from $0.00 to $0.16)
- **Control group change:** +$0.05 (from $0.00 to $0.05)
- **Average Treatment Effect:** **$0.11 per user**
- **95% Confidence Interval:** [$0.04, $0.18]
- **Statistical Significance:** p = 0.003 (significant)

**Balance Check:** ✓ PASSED  
All users had $0 pre-campaign spending (by design - they were inactive), confirming proper targeting.

### 3. Caveats & Limitations
⚠️ **MODERATE CONCERNS**

1. **Small Effect Size:** While statistically significant, the $0.11 spending increase is modest

2. **Short-Term Measurement:** We only observe one month post-campaign. Key questions:
   - Do reactivated users stay active?
   - What is their lifetime value?

3. **Low Base Reactivation:** Even with treatment, only 15.6% reactivated - 84% still inactive

4. **Cost-Benefit Unclear:** Need to compare campaign cost to long-term value of reactivated users

### 4. Recommendation
**OPTIMIZE BEFORE SCALING** - The campaign successfully reactivates users, but the immediate financial return is small.

**Next Steps:**
1. **Track long-term retention:** Measure 3-month and 6-month retention of reactivated users
2. **Calculate customer lifetime value (CLV):** If reactivated users have high CLV, the campaign may be worthwhile despite low immediate spending
3. **Test variations:**
   - Different messaging or incentives
   - Targeting users inactive for different durations (30 days vs 60 days vs 90 days)
   - Multi-touch campaigns vs single email

**Estimated ROI:** ~10% immediate return (assuming $0.10 email cost), but potentially much higher if reactivated users have strong retention

---

## Methodology Summary

### Causal Inference Framework

We used different methods for different campaign designs:

| Design Type | Method | Campaigns | Confidence Level |
|-------------|--------|-----------|------------------|
| **Randomized** | A/B Test | C001, C004 | ★★★ High |
| **Targeted** | Regression | C002 | ★★☆ Medium |
| **Geographic** | Diff-in-Diff | C003 | ★★★ High |

### Why Different Methods?

**The Gold Standard: Randomization (C001, C004)**
- Random assignment ensures treatment and control groups are identical *on average*
- Any difference in outcomes is causally attributable to the campaign
- No confounding, no selection bias
- **Limitation:** Not always feasible (can't randomize geography, may not want to withhold treatment from high-value users)

**When Randomization Isn't Possible: Quasi-Experimental Methods**

**Regression with Controls (C002):**
- Used when treatment is targeted based on observable characteristics
- Controls for confounders statistically
- **Limitation:** Can only control for measured variables; unmeasured confounders remain

**Difference-in-Differences (C003):**
- Used for geographic or time-based rollouts
- Controls for time-invariant differences between groups
- **Limitation:** Assumes parallel trends; vulnerable to time-varying confounders

---

## Investment Recommendations for Q1 2025

### Priority 1: SCALE UP
**C001 - Spring Email Blast** ($4.44 effect, high confidence)
- Increase frequency (monthly → bi-weekly)
- Expand to larger audience segments
- Test variations (subject lines, content, timing)

**C003 - West Coast Regional Push** ($3.11 effect, high confidence)
- Roll out to East Coast and Midwest
- Maintain mixed-channel approach
- Monitor for saturation effects

### Priority 2: OPTIMIZE
**C004 - Win-Back Campaign** ($0.11 effect, but strategic value)
- Continue current campaign (low cost, positive effect)
- Test enhanced versions with incentives
- Track long-term CLV to assess true ROI

### Priority 3: VALIDATE
**C002 - Premium Upsell** ($2.87 effect, medium confidence)
- Run randomized A/B test within high-spender segment
- Test on medium spenders to find optimal targeting
- Validate causal effect before major investment

### Budget Allocation Recommendation

Based on effect sizes and confidence levels:

| Campaign | Q1 Budget % | Rationale |
|----------|-------------|-----------|
| C001 Email Blast | **40%** | Highest ROI, proven causal effect |
| C003 Regional Expansion | **35%** | Strong effect, growth opportunity |
| C004 Win-Back | **10%** | Low cost, strategic retention value |
| C002 Upsell Testing | **15%** | Validation phase before scaling |

---

## Technical Appendix

### Statistical Tests Performed

**C001 (A/B Test):**
- Two-sample t-test for difference in means
- Balance check on pre-campaign covariates
- 95% confidence intervals using normal approximation

**C002 (Regression):**
- Ordinary Least Squares (OLS) regression
- Model: Change ~ Treatment + Pre_Campaign_Spending
- Heteroskedasticity-robust standard errors

**C003 (Difference-in-Differences):**
- Two-sample t-test on changes
- Parallel trends test on pre-campaign levels
- 95% confidence intervals using normal approximation

**C004 (A/B Test):**
- Two-sample t-test for continuous outcome (spending)
- Chi-square test for binary outcome (reactivation)
- 95% confidence intervals using normal approximation

### Assumptions & Diagnostics

**All Analyses:**
- ✓ Independence of observations (different users)
- ✓ Sufficient sample sizes for central limit theorem
- ✓ No obvious outliers driving results

**C001 & C004 (Randomized):**
- ✓ Balance checks passed
- ✓ No evidence of contamination

**C002 (Regression):**
- ⚠️ Linearity assumption (reasonable but not perfect)
- ⚠️ Potential unmeasured confounders

**C003 (DiD):**
- ✓ Parallel trends supported (pre-campaign balance)
- ⚠️ Cannot rule out time-varying confounders

---

## Conclusion

This analysis demonstrates the importance of **matching analytical methods to campaign designs**. Randomized campaigns (C001, C004) provide the cleanest causal estimates, while observational campaigns (C002, C003) require more sophisticated methods and come with additional assumptions.

**Key Takeaway for Future Campaigns:**
- **Design for causal inference from the start**
- Randomize whenever possible
- When randomization isn't feasible, plan for quasi-experimental methods (DiD, regression discontinuity, etc.)
- Always collect pre-campaign data for controls and balance checks

**For Q1 2025:** Focus investment on C001 and C003, which show strong, credible causal effects. Use C004 strategically for retention, and validate C002 with proper randomization before scaling.

---

**Questions or need additional analysis?** Contact the analytics team.

*Analysis conducted using difference-in-means tests, OLS regression, and difference-in-differences estimation. All code and data available for replication.*
