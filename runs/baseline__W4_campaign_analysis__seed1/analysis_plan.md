# Marketing Campaign Causal Impact Analysis Plan

**Prepared for:** Marketing Director  
**Date:** Analysis of Q2-Q4 2024 Campaigns  
**Objective:** Measure causal impact of marketing campaigns and provide investment recommendations for next quarter

---

## Executive Summary

We analyzed four marketing campaigns using appropriate causal inference methods based on each campaign's design. Our analysis reveals:

- **C004 (Win-Back Campaign)**: Strongest causal evidence with 10.8 percentage point reactivation lift (p=0.005)
- **C001 (Spring Email Blast)**: Positive $4.44 effect but not statistically significant; needs larger sample
- **C002 (Premium Upsell)**: ~$16 effect estimated, but high uncertainty due to selection bias
- **C003 (West Coast Regional)**: ~$3 effect estimated, but confounded by regional differences

**Key Recommendation:** Prioritize Win-Back campaigns and run properly randomized tests for other initiatives before scaling.

---

## Campaign C001: Spring Email Blast

### 1. Data Type & Design
**Type:** Experimental (Randomized Controlled Trial)
- **Assignment:** Random assignment to 50% of active users
- **Sample Size:** 710 users (359 exposed, 351 control)
- **Period:** April 2024
- **Outcome:** Monthly spend

### 2. Analytical Method
**Primary Method:** Standard A/B Test Analysis with Difference-in-Differences

**Why this method:**
- Random assignment ensures treatment and control groups are comparable
- Pre-campaign balance check confirms randomization worked (difference: -$0.03)
- DiD accounts for any time trends affecting both groups

**Analysis:**
```
Exposed Group:  Pre: $28.11 → Post: $32.86 (Change: +$4.75)
Control Group:  Pre: $28.14 → Post: $28.45 (Change: +$0.31)

Average Treatment Effect (ATE): $4.41
Difference-in-Differences: $4.44
95% Confidence Interval: [-$4.74, $13.56]
Statistical Significance: p = 0.346 (not significant at α=0.05)
```

### 3. Preliminary Estimates
- **Effect Size:** $4.44 per user per month
- **12-Month Revenue Impact:** ~$19,147 (if effect persists)
- **ROI (12-month):** 283% (assuming $5,000 campaign cost)

### 4. Caveats & Limitations
⚠️ **Key Limitations:**
- **Not statistically significant** - Could be due to:
  - True effect is small
  - Sample size too small (power issue)
  - High variance in spending behavior
- **Effect persistence unknown** - We only observe one month post-campaign
- **Spillover effects** - Email recipients might influence non-recipients

**Confidence Level:** 🟡 Moderate (65%) - Clean design but underpowered

### 5. Recommendations
1. ✅ **Run larger test** with 1,500+ users to achieve 80% power
2. ✅ **Track long-term effects** to measure persistence
3. ✅ **Segment analysis** to identify which user types respond best
4. ⚠️ **Don't scale yet** - Wait for statistically significant results

---

## Campaign C002: Premium Upsell Push

### 1. Data Type & Design
**Type:** Observational (Targeted Campaign)
- **Assignment:** Targeted at high-spend users (>$80/month)
- **Sample Size:** 144 users (72 exposed, 72 control)
- **Period:** June 2024
- **Outcome:** Monthly spend

### 2. Analytical Method
**Primary Method:** Difference-in-Differences + Propensity Score Matching

**Why this method:**
- **NOT randomized** - Exposed group selected based on high prior spending
- Naive comparison would be severely biased
- DiD controls for pre-existing differences
- Matching improves balance on pre-campaign spending

**Analysis:**
```
Pre-Campaign Balance Check:
  Exposed: $200.35  |  Control: $64.77  |  Difference: $135.59 ⚠️

Naive ATE: $145.35 (BIASED - don't use!)
DiD Estimate: $9.76
Matched DiD Estimate: $16.48 (PREFERRED)
```

### 3. Preliminary Estimates
- **Best Estimate:** $16.48 per user per month (matched DiD)
- **12-Month Revenue Impact:** ~$14,238
- **ROI (12-month):** 78% (assuming $8,000 campaign cost)

### 4. Caveats & Limitations
⚠️ **Critical Limitations:**
- **Selection bias** - Exposed users fundamentally different (2-3x higher baseline spending)
- **Regression to the mean** - High spenders may naturally decrease
- **Matching imperfect** - Still $121 difference after matching
- **Small sample** - Only 72 treated users
- **Unobserved confounders** - May be other differences we can't measure

**Confidence Level:** 🔴 Low (60%) - Observational design with strong selection bias

### 5. Recommendations
1. 🚫 **DO NOT scale based on current data** - Too much uncertainty
2. ✅ **Run proper randomized A/B test** among high-spend users
3. ✅ **Use regression adjustment** with more covariates if available
4. ✅ **Consider instrumental variables** if natural experiment exists
5. ⚠️ **Treat $16 estimate as upper bound** - Likely overestimate due to residual bias

---

## Campaign C003: West Coast Regional Push

### 1. Data Type & Design
**Type:** Quasi-Experimental (Geographic Rollout)
- **Assignment:** All West Coast users exposed, others as control
- **Sample Size:** 1,000 users (274 exposed, 726 control)
- **Period:** July-August 2024
- **Outcome:** Monthly spend

### 2. Analytical Method
**Primary Method:** Difference-in-Differences

**Why this method:**
- Geographic assignment creates natural experiment
- DiD controls for fixed regional differences
- Assumes parallel trends (regions would have changed similarly without campaign)

**Analysis:**
```
Pre-Campaign Baseline:
  West Coast: $31.47  |  Other Regions: $27.70  |  Difference: $3.77

Post-Campaign:
  West Coast: $35.23  |  Other Regions: $28.35

Naive ATE: $6.88 (BIASED)
DiD Estimate: $3.11 (PREFERRED)
```

### 3. Preliminary Estimates
- **Effect Size:** $3.11 per user per month
- **12-Month Revenue Impact:** ~$10,237
- **ROI (12-month):** -15% (assuming $12,000 campaign cost)

### 4. Caveats & Limitations
⚠️ **Key Limitations:**
- **Parallel trends assumption** - May not hold if:
  - West Coast has different seasonal patterns
  - Economic conditions differ by region
  - Product-market fit varies geographically
- **Pre-existing differences** - West Coast users already spent $3.77 more
- **Spillover effects** - Regional campaigns might affect neighboring areas
- **Time-varying confounders** - Other events during July-August
- **SUTVA violation** - Users may travel between regions

**Confidence Level:** 🟡 Moderate (75%) - DiD reasonable but assumptions questionable

### 5. Recommendations
1. ✅ **Validate parallel trends** - Check pre-campaign trends over multiple periods
2. ✅ **Synthetic control method** - Create better counterfactual using multiple control regions
3. ✅ **Event study analysis** - Plot effects over time to check for pre-trends
4. ⚠️ **Consider randomized geo-experiment** - Randomly assign regions in future
5. 📊 **Collect more data** - Need longer time series to validate assumptions

---

## Campaign C004: Win-Back Campaign

### 1. Data Type & Design
**Type:** Experimental (Randomized Controlled Trial)
- **Assignment:** Random assignment to 50% of inactive users (60+ days)
- **Sample Size:** 290 users (147 exposed, 143 control)
- **Period:** September 2024
- **Outcome:** Reactivation (return to spending)

### 2. Analytical Method
**Primary Method:** A/B Test with Binary Outcome Analysis

**Why this method:**
- Clean randomization among inactive users
- Perfect balance on pre-campaign spending (both groups at $0)
- Binary outcome (reactivated vs. not) plus continuous spending

**Analysis:**
```
Reactivation Rates:
  Exposed: 23/147 = 15.6%
  Control: 7/143 = 4.9%
  
Reactivation Lift: 10.8 percentage points
Chi-square test: χ² = 7.91, p = 0.005 ✓ SIGNIFICANT

Average Spend (Post-Campaign):
  Exposed: $0.16
  Control: $0.05
  Difference: $0.11 (p = 0.003) ✓ SIGNIFICANT
```

### 3. Preliminary Estimates
- **Reactivation Effect:** 10.8 percentage points (95% CI: [3.9pp, 17.6pp])
- **Spend Effect:** $0.11 per user per month
- **Note:** Low absolute spend because most users remain inactive

### 4. Caveats & Limitations
⚠️ **Limitations:**
- **Low absolute revenue** - Most reactivated users spend little initially
- **Long-term value unknown** - Need to track reactivated users over time
- **Definition of inactive** - 60+ days may include different user types
- **Seasonal effects** - September timing may matter

**Confidence Level:** 🟢 High (90%) - Strong experimental design with significant results

### 5. Recommendations
1. ✅ **SCALE IMMEDIATELY** - Strongest causal evidence of all campaigns
2. ✅ **Expand to all inactive users** - Clear positive effect
3. ✅ **Track lifetime value** - Measure long-term value of reactivated users
4. ✅ **Test variations** - Experiment with different messaging, timing, incentives
5. ✅ **Segment analysis** - Identify which inactive users respond best
6. 📊 **Calculate true ROI** - Current analysis shows low immediate spend, but LTV likely higher

---

## Comparative Summary

| Campaign | Design Type | Method | Effect Estimate | Confidence | Statistical Sig. | Recommendation |
|----------|-------------|--------|-----------------|------------|------------------|----------------|
| **C001** Spring Email | Randomized | A/B Test + DiD | $4.44/user/mo | 🟡 Moderate (65%) | No (p=0.35) | Run larger test |
| **C002** Premium Upsell | Targeted | Matched DiD | $16.48/user/mo | 🔴 Low (60%) | Unknown | Randomize first |
| **C003** West Coast | Geo-rollout | DiD | $3.11/user/mo | 🟡 Moderate (75%) | Unknown | Validate assumptions |
| **C004** Win-Back | Randomized | A/B Test | 10.8pp reactivation | 🟢 High (90%) | Yes (p=0.005) | **SCALE NOW** |

---

## Investment Recommendations for Next Quarter

### Priority 1: Win-Back Campaigns (C004) 🟢
**Action:** Scale to all inactive users (60+ days)

**Rationale:**
- Strongest causal evidence (randomized, p=0.005)
- 3x reactivation rate vs. control (15.6% vs. 4.9%)
- Low cost per user ($3,000 for 290 users = $10/user)
- High strategic value (customer retention)

**Investment:** Increase budget 5-10x to reach all inactive users

---

### Priority 2: Email Campaigns (C001) 🟡
**Action:** Run larger randomized test before scaling

**Rationale:**
- Clean experimental design
- Positive trend ($4.44 effect) but not significant
- Likely underpowered (need ~1,500 users for 80% power)
- Low cost channel (email)

**Investment:** $10,000 for properly powered test

---

### Priority 3: Premium Upsell (C002) 🔴
**Action:** Run proper A/B test; don't scale current approach

**Rationale:**
- Current data has severe selection bias
- Effect estimate highly uncertain ($10-$16 range)
- Can't make causal claims from observational data
- High-value segment worth testing properly

**Investment:** $15,000 for randomized test among high-spend users

---

### Priority 4: Regional Campaigns (C003) ⚠️
**Action:** Validate with better methods before expansion

**Rationale:**
- Geographic confounding likely
- Parallel trends assumption questionable
- Negative ROI in current analysis
- Need synthetic control or randomized geo-test

**Investment:** $5,000 for analytical validation; hold on expansion

---

## Methodological Recommendations for Future Campaigns

### 1. Always Randomize When Possible
- Randomization is the gold standard for causal inference
- Even small randomized tests beat large observational studies
- Use stratified randomization to improve precision

### 2. Measure Pre-Campaign Baselines
- Essential for DiD and balance checks
- Helps detect selection bias
- Enables better effect estimation

### 3. Plan for Adequate Sample Sizes
- Use power analysis before launching
- Target 80% power to detect meaningful effects
- Account for variance in your metrics

### 4. Track Long-Term Outcomes
- Campaign effects may persist or decay
- Lifetime value matters more than immediate impact
- Watch for delayed effects (e.g., word-of-mouth)

### 5. Document Assignment Mechanisms
- Clear documentation enables proper analysis
- Record all targeting rules and exclusions
- Track exposure timing precisely

### 6. Consider Spillover Effects
- Campaigns may affect non-exposed users
- Geographic/network spillovers violate SUTVA
- Use cluster randomization when appropriate

---

## Technical Appendix: Statistical Methods

### A/B Test Analysis (C001, C004)
- **Estimand:** Average Treatment Effect (ATE)
- **Estimator:** Difference in means (post-campaign)
- **Inference:** Two-sample t-test
- **Assumptions:** Random assignment, SUTVA, no interference

### Difference-in-Differences (All Campaigns)
- **Estimand:** ATT (Average Treatment Effect on Treated)
- **Estimator:** (Ȳ_post^T - Ȳ_pre^T) - (Ȳ_post^C - Ȳ_pre^C)
- **Assumptions:** Parallel trends, no compositional changes
- **Advantage:** Controls for time-invariant confounders

### Propensity Score Matching (C002)
- **Method:** Nearest-neighbor matching on pre-campaign spend
- **Purpose:** Reduce selection bias
- **Limitation:** Only controls for observed confounders
- **Result:** Improved balance but still imperfect

---

## Data Quality Notes

✅ **Strengths:**
- Clean assignment indicators (exposed/not exposed)
- Pre and post measurements available
- Reasonable sample sizes for most campaigns
- Clear campaign periods

⚠️ **Limitations:**
- Only one post-period measured (can't assess persistence)
- No user-level covariates for adjustment
- Potential measurement error in spend data
- Missing data for some users (70 users in users.csv have missing spend)

---

## Conclusion

Our analysis demonstrates the critical importance of experimental design in measuring campaign effectiveness. The Win-Back campaign (C004) provides the clearest evidence of impact due to its randomized design, while the targeted Premium Upsell campaign (C002) remains highly uncertain despite showing large effects.

**Key Takeaway:** Invest in proper randomization upfront. The cost of running an A/B test is far less than the cost of scaling an ineffective campaign or missing opportunities with effective ones.

**Next Steps:**
1. Scale Win-Back campaigns immediately
2. Run properly powered tests for Email and Premium Upsell
3. Validate Regional campaign with better methods
4. Implement systematic A/B testing framework for all future campaigns

---

*For questions about this analysis, please contact the Data Science team.*
