# Marketing Campaign Causal Impact Analysis Plan

**Prepared for:** Marketing Director  
**Date:** 2024  
**Objective:** Measure the causal impact of Q2-Q3 2024 marketing campaigns and provide recommendations for Q4 investment

---

## Executive Summary

We analyzed four marketing campaigns conducted in 2024 using appropriate causal inference methods based on each campaign's design. **Three campaigns (C001, C003, C004) show strong positive effects with high causal validity**, while one campaign (C002) shows positive results but requires cautious interpretation due to methodological limitations.

### Key Findings:
- **C001 (Spring Email Blast)**: +$4.44/month per user, highly reliable (randomized)
- **C002 (Premium Upsell)**: +$9.76/month per user, but likely overestimated (selection bias)
- **C003 (West Coast Regional)**: +$3.11/month per user, reliable with caveats (geographic)
- **C004 (Win-Back Campaign)**: +10.8 percentage points reactivation, highly reliable (randomized)

### Investment Recommendations:
1. **SCALE UP**: C001 (Spring Email Blast) - proven ROI with clean experimental design
2. **SCALE UP**: C004 (Win-Back Campaign) - strong reactivation effect
3. **TEST FURTHER**: C002 (Premium Upsell) - promising but needs proper A/B test
4. **EXPAND CAUTIOUSLY**: C003 (West Coast Regional) - positive but verify with other regions

---

## Campaign 1: Spring Email Blast (C001)

### Campaign Overview
- **Period:** April 1-30, 2024
- **Channel:** Email
- **Target:** All active users
- **Sample Size:** 710 users (359 treatment, 351 control)

### Data Type: Experimental (Randomized A/B Test)
This campaign used **random assignment** of eligible users to treatment (50%) and control (50%) groups. This is the gold standard for causal inference.

### Analytical Method: A/B Test Analysis with Difference-in-Differences

**Why this method?**
- Random assignment ensures treatment and control groups are comparable
- Pre-campaign data allows us to verify balance and improve precision
- Difference-in-differences (DiD) controls for any baseline differences

**Analysis:**
```
Pre-campaign balance check:
  Treatment: $28.11/month
  Control:   $28.14/month
  Difference: -$0.03 ✓ (groups are balanced)

Post-campaign outcomes:
  Treatment: $32.86/month
  Control:   $28.45/month
  
Treatment Effect (DiD):
  Treatment change: +$4.75
  Control change:   +$0.31
  Causal effect:    +$4.44/month per user
  
Statistical significance: p < 0.001 ***
```

### Preliminary Estimates
- **Treatment Effect:** +$4.44 per user per month
- **Statistical Significance:** Highly significant (p < 0.001)
- **Confidence:** 95% confidence interval approximately [$3.35, $5.53]
- **Estimated Annual Revenue Impact:** $19,147 (based on 359 users)

### Caveats and Limitations
1. ✓ **Minimal concerns** - this is a well-designed randomized experiment
2. **External validity:** Results apply to "active users" - may not generalize to inactive users
3. **Seasonality:** Campaign ran in April (spring) - effects might differ in other seasons
4. **Long-term effects:** We only observe one month post-campaign; effects may decay or compound over time

### Recommendation
**STRONG INVEST** - This campaign has the strongest causal evidence. The randomized design gives us high confidence that the $4.44 monthly lift is a true causal effect. Consider:
- Scaling to full active user base
- Testing in different seasons to verify consistency
- Monitoring long-term retention of the spending increase

---

## Campaign 2: Premium Upsell Push (C002)

### Campaign Overview
- **Period:** June 1-30, 2024
- **Channel:** In-app messaging
- **Target:** High-spend users (>$80/month in prior period)
- **Sample Size:** 144 users (72 treatment, 72 control)

### Data Type: Observational (Targeted, Non-Random Assignment)

⚠️ **CRITICAL ISSUE:** This campaign used **targeted assignment**, not randomization. The notes indicate users were selected based on prior spending (>$80/month). This creates **selection bias** that threatens causal interpretation.

### Analytical Method: Difference-in-Differences with Strong Caveats

**Why this method?**
- DiD can help control for baseline differences
- However, it cannot fully eliminate selection bias from non-random assignment
- The "control" group may differ systematically from treatment group

**Analysis:**
```
Pre-campaign balance check:
  Treatment: $200.35/month
  Control:   $64.77/month
  Difference: +$135.59 ⚠️ LARGE IMBALANCE!

This confirms non-random assignment - treatment group had 
much higher baseline spending.

Post-campaign outcomes:
  Treatment: $210.07/month
  Control:   $64.73/month
  
Difference-in-Differences:
  Treatment change: +$9.72
  Control change:   -$0.04
  DiD estimate:     +$9.76/month per user
  
Statistical significance: p < 0.001 ***
```

### Preliminary Estimates
- **DiD Estimate:** +$9.76 per user per month
- **Statistical Significance:** Highly significant (p < 0.001)
- **Estimated Annual Revenue Impact:** $8,434 (based on 72 users)
- **⚠️ CAUTION:** This estimate is likely **biased upward** due to selection effects

### Caveats and Limitations
1. **MAJOR CONCERN - Selection Bias:** Treatment group was selected based on high prior spending
   - These users may have different growth trajectories regardless of campaign
   - The control group is not truly comparable (much lower baseline spending)
   - DiD helps but cannot fully eliminate this bias

2. **Regression to the mean:** High spenders selected for treatment may naturally decrease over time, while the observed increase could be:
   - Smaller than it appears (if natural decrease was prevented)
   - Or larger than it appears (if natural decrease was overcome)

3. **Small sample size:** Only 144 users total limits statistical power

4. **Confounding:** We don't know what else differs between treatment and control groups besides the campaign

### Recommendation
**TEST PROPERLY BEFORE SCALING** - While the results look promising (+$9.76/month), we **cannot confidently attribute this to the campaign** due to selection bias. 

**Action items:**
1. **Run a proper randomized A/B test** with high-spend users randomly assigned to treatment/control
2. Consider **propensity score matching** to create a more comparable control group from historical data
3. If re-running as A/B test, expect the true effect to be **smaller** than $9.76/month
4. Do NOT scale this campaign based on current evidence alone

**Alternative analysis approach:**
- Match treatment users to similar control users based on:
  - Prior spending levels
  - Tenure
  - Plan tier
  - Engagement metrics
- This would provide a more credible estimate, though still not as strong as randomization

---

## Campaign 3: West Coast Regional Push (C003)

### Campaign Overview
- **Period:** July 1 - August 31, 2024
- **Channel:** Mixed (email, in-app, social)
- **Target:** West region users
- **Sample Size:** 1,000 users (274 West region, 726 other regions)

### Data Type: Quasi-Experimental (Geographic Rollout)

This campaign used a **geographic rollout** design, where the West region received the campaign while other regions did not. This is a quasi-experimental design that allows for causal inference under certain assumptions.

### Analytical Method: Difference-in-Differences (DiD)

**Why this method?**
- DiD is the standard approach for geographic rollouts
- Compares the change in West region to the change in other regions
- Controls for time trends that affect all regions similarly

**Key Assumption:** **Parallel trends** - West and other regions would have changed similarly in the absence of the campaign.

**Analysis:**
```
Pre-campaign balance check:
  West region:    $31.47/month
  Other regions:  $27.70/month
  Difference:     +$3.77 (West slightly higher at baseline)

Post-campaign outcomes:
  West region:    $35.23/month
  Other regions:  $28.35/month
  
Difference-in-Differences:
  West change:    +$3.76
  Other change:   +$0.64
  DiD estimate:   +$3.11/month per user
  
Statistical significance: p < 0.001 ***
```

### Preliminary Estimates
- **Treatment Effect (DiD):** +$3.11 per user per month
- **Statistical Significance:** Highly significant (p < 0.001)
- **Estimated Annual Revenue Impact:** $10,237 (for West region users)

### Caveats and Limitations

1. **Parallel Trends Assumption:** 
   - We assume West and other regions would have trended similarly without the campaign
   - **Cannot fully verify** this assumption with only pre/post data
   - Regional differences in seasonality, economic conditions, or user composition could violate this
   - West region had slightly higher baseline spending ($3.77 difference)

2. **Geographic Confounding:**
   - Other events specific to West region during July-August could explain the effect
   - Examples: regional economic changes, competitor actions, local events

3. **Spillover Effects:**
   - If users in other regions were exposed to the campaign (e.g., via social media), the control group is contaminated
   - This would **underestimate** the true effect

4. **Sample Composition:**
   - West region is only 27.4% of sample - may not be representative
   - Results may not generalize to other regions

### Recommendation
**EXPAND WITH VALIDATION** - The DiD estimate of +$3.11/month is credible but not as strong as a randomized experiment.

**Action items:**
1. **Validate with additional regions:** Roll out to another region (e.g., East Coast) and verify similar effects
2. **Check for pre-trends:** If possible, examine whether West and other regions had parallel trends in months before the campaign
3. **Monitor for spillover:** Verify that other regions weren't exposed to campaign elements
4. **Consider staggered rollout:** Roll out to different regions at different times to strengthen causal inference

**If validation is successful:** Scale to all regions with confidence in the +$3.11/month effect.

---

## Campaign 4: Win-Back Campaign (C004)

### Campaign Overview
- **Period:** September 1-30, 2024
- **Channel:** Email
- **Target:** Inactive users (60+ days without activity)
- **Sample Size:** 290 users (147 treatment, 143 control)

### Data Type: Experimental (Randomized A/B Test)

This campaign used **random assignment** of inactive users to treatment (50%) and control (50%) groups. This provides strong causal evidence.

### Analytical Method: A/B Test for Binary Outcome (Reactivation)

**Why this method?**
- Random assignment ensures comparability
- Outcome is binary (reactivated or not), so we use proportion tests
- Chi-square test for statistical significance

**Analysis:**
```
Reactivation rates:
  Treatment: 23/147 = 15.6%
  Control:   7/143  = 4.9%
  
Treatment Effect:
  Absolute lift: +10.8 percentage points
  Relative lift: +219.6% (more than 3x the control rate)
  
Statistical significance: p = 0.005 **
```

### Preliminary Estimates
- **Reactivation Lift:** +10.8 percentage points (15.6% vs 4.9%)
- **Relative Improvement:** 220% increase over control
- **Statistical Significance:** Significant at 1% level (p = 0.005)
- **Estimated Annual Revenue Impact:** $190 (based on $1/month average spend per reactivated user)

**Note on revenue impact:** Reactivated users currently spend only $1/month on average. The value of this campaign is in:
1. Preventing churn and maintaining user base
2. Potential for these users to increase spending over time
3. Lifetime value beyond the first month

### Caveats and Limitations

1. **Low absolute reactivation rate:** Even with treatment, only 15.6% reactivated
   - 84.4% of inactive users remained inactive despite the campaign
   - Consider whether this is cost-effective

2. **Low spending among reactivated users:** 
   - Reactivated users spend only $1/month on average
   - Need to track whether spending increases over subsequent months
   - Lifetime value analysis needed for full ROI assessment

3. **Sample size:** 290 users is adequate for detecting the observed effect, but:
   - Confidence intervals are wider than for larger samples
   - Subgroup analysis (e.g., by inactivity duration) would have limited power

4. **Short-term outcome:** 
   - We only observe one month post-campaign
   - Some reactivated users may churn again quickly
   - Need to track 3-month and 6-month retention

5. **Definition of "inactive":**
   - Campaign targeted users inactive for 60+ days
   - Results may differ for users inactive for shorter/longer periods

### Recommendation
**INVEST AND OPTIMIZE** - This campaign shows a clear, statistically significant effect on reactivation with strong causal evidence.

**Action items:**
1. **Continue the campaign** - The 10.8pp lift is meaningful for preventing churn
2. **Track long-term value:**
   - Monitor 3-month and 6-month retention of reactivated users
   - Track spending growth among reactivated users
   - Calculate true lifetime value to assess ROI

3. **Optimize the campaign:**
   - Test different messaging to improve the 15.6% reactivation rate
   - Segment by inactivity duration (60-90 days vs 90+ days)
   - Test different incentives or offers

4. **Cost-benefit analysis:**
   - Calculate cost per reactivation
   - Compare to customer acquisition cost (CAC)
   - If reactivation cost < CAC, this is highly valuable

5. **Expand targeting:**
   - Consider users inactive for 30-60 days (earlier intervention)
   - Test whether effects differ by user segment

---

## Comparative Analysis and Investment Priorities

### Campaign Effectiveness Summary

| Campaign | Treatment Effect | Causal Validity | Statistical Sig. | Est. Annual Revenue |
|----------|-----------------|-----------------|------------------|---------------------|
| **C001: Spring Email** | +$4.44/month | ⭐⭐⭐ High | p < 0.001 *** | $19,147 |
| **C002: Premium Upsell** | +$9.76/month | ⭐ Low-Medium | p < 0.001 *** | $8,434 (likely overstated) |
| **C003: West Regional** | +$3.11/month | ⭐⭐ Medium | p < 0.001 *** | $10,237 |
| **C004: Win-Back** | +10.8pp reactivation | ⭐⭐⭐ High | p = 0.005 ** | $190 (+ LTV) |

### Investment Recommendations for Next Quarter

#### Tier 1: High Confidence - Scale Immediately
1. **C001 (Spring Email Blast)** - $4.44/month lift
   - ✅ Randomized design = high causal validity
   - ✅ Large sample size
   - ✅ Highly significant results
   - **Action:** Scale to full active user base, test quarterly cadence

2. **C004 (Win-Back Campaign)** - 10.8pp reactivation lift
   - ✅ Randomized design = high causal validity
   - ✅ Addresses churn (strategic priority)
   - ✅ Significant results
   - **Action:** Continue monthly, optimize messaging, track LTV

#### Tier 2: Promising but Needs Validation
3. **C002 (Premium Upsell Push)** - $9.76/month lift (uncertain)
   - ⚠️ Selection bias threatens validity
   - ✅ Large effect size if real
   - **Action:** Run proper randomized A/B test before scaling
   - **Expected:** True effect likely smaller than $9.76

4. **C003 (West Coast Regional)** - $3.11/month lift
   - ⚠️ Geographic design has assumptions
   - ✅ Significant positive effect
   - **Action:** Validate with rollout to another region
   - **If validated:** Scale nationally

### Budget Allocation Recommendation

If you have $100 to allocate across campaigns:
- **$40** - C001 (Spring Email) - Scale to full user base
- **$30** - C004 (Win-Back) - Continue and optimize
- **$20** - C002 (Premium Upsell) - Run proper A/B test
- **$10** - C003 (West Regional) - Validate in another region

### Key Methodological Lessons

1. **Randomization is gold:** C001 and C004 provide the strongest evidence because of random assignment
2. **Selection bias is serious:** C002 shows why targeted campaigns need careful analysis
3. **Geographic designs work but need validation:** C003 is credible but requires parallel trends assumption
4. **Pre-campaign data is valuable:** Allows balance checks and DiD estimation

---

## Technical Appendix: Analytical Methods Explained

### A/B Testing (Used for C001, C004)
- **When to use:** Randomized experiments
- **How it works:** Compare outcomes between randomly assigned treatment and control groups
- **Assumptions:** Random assignment, no spillover between groups
- **Advantages:** Strongest causal inference, simple interpretation
- **Limitations:** Requires ability to randomize, may not capture long-term effects

### Difference-in-Differences (Used for C001, C002, C003)
- **When to use:** When you have pre/post data for treatment and control groups
- **How it works:** Compares the change in treatment group to change in control group
- **Formula:** DiD = (Y_treatment_post - Y_treatment_pre) - (Y_control_post - Y_control_pre)
- **Assumptions:** Parallel trends (groups would change similarly without treatment)
- **Advantages:** Controls for baseline differences, time trends
- **Limitations:** Parallel trends assumption may not hold

### Propensity Score Matching (Recommended for C002)
- **When to use:** Observational data with selection bias
- **How it works:** Match treatment units to similar control units based on observable characteristics
- **Assumptions:** Selection on observables (no unobserved confounders)
- **Advantages:** Creates more comparable groups
- **Limitations:** Cannot control for unobserved differences, requires rich covariate data

---

## Data Quality and Limitations

### Overall Data Quality: Good
- ✅ Clear campaign assignment indicators
- ✅ Pre and post-campaign measurements
- ✅ Reasonable sample sizes
- ✅ Low missing data

### Limitations:
1. **Short time horizon:** Only one month post-campaign for most outcomes
2. **Limited covariates:** Could benefit from more user characteristics for matching/regression
3. **No cost data:** Cannot calculate full ROI without campaign costs
4. **No long-term tracking:** Need 3-6 month follow-up for sustained effects

---

## Next Steps and Future Analysis

### Immediate Actions:
1. **Implement recommendations** for each campaign (see individual sections)
2. **Set up tracking** for long-term effects (3-month, 6-month outcomes)
3. **Run proper A/B test** for C002 (Premium Upsell)
4. **Validate C003** with additional geographic rollout

### Future Analytical Enhancements:
1. **Heterogeneous treatment effects:** Analyze whether campaigns work differently for different user segments
2. **Cost-benefit analysis:** Incorporate campaign costs to calculate true ROI
3. **Lifetime value modeling:** Track long-term value of acquired/reactivated users
4. **Attribution modeling:** If users exposed to multiple campaigns, disentangle effects
5. **Optimal targeting:** Use machine learning to identify which users benefit most from each campaign

### Recommended Data Collection:
1. **Campaign costs:** Track spending on each campaign for ROI calculation
2. **User characteristics:** Collect more covariates (engagement metrics, demographics) for better matching
3. **Long-term outcomes:** Track users for 6+ months post-campaign
4. **Intermediate metrics:** Track engagement, not just spending (e.g., logins, feature usage)

---

## Conclusion

We have strong evidence that **three of four campaigns (C001, C003, C004) had positive causal effects** on their intended outcomes. The Spring Email Blast and Win-Back Campaign are particularly strong candidates for continued investment due to their randomized designs. The Premium Upsell Push shows promise but requires a proper randomized test before scaling. The West Coast Regional Push should be validated in other regions before national rollout.

**Overall recommendation:** Marketing campaigns are working, but investment decisions should be guided by the strength of causal evidence, not just statistical significance. Prioritize campaigns with randomized designs and validate quasi-experimental results before major scaling.

---

**Prepared by:** Data Science Team  
**Contact:** For questions about methodology or additional analysis requests  
**Last Updated:** 2024

---

## Visualizations

See accompanying PNG files:
- `campaign_performance_overview.png` - Summary of all campaign effects
- `treatment_effect_distributions.png` - Distribution of outcomes by campaign
- `campaign_effects_summary.png` - Comparative effect sizes
- `c002_selection_bias.png` - Evidence of selection bias in C002
