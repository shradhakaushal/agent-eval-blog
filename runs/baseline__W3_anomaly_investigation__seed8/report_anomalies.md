# Sensor Anomaly Detection Report

## Executive Summary
Analysis of 30 days of sensor data (720 readings per sensor) has identified **Sensor 3** as malfunctioning. The sensor exhibits severe temperature measurement anomalies including elevated readings, excessive variability, and progressive drift over time.

## 1. Problematic Sensor Identification

**Sensor 3 is malfunctioning.**

## 2. Evidence Supporting This Conclusion

### 2.1 Statistical Anomalies

| Metric | Sensor 3 | Baseline (Sensors 1,2,4,5) | Deviation |
|--------|----------|---------------------------|-----------|
| Mean Temperature | 24.41°C | 22.00°C | +2.41°C (+11%) |
| Std Deviation | 3.38°C | 0.30°C | **11.4x higher** |
| Maximum Reading | 33.62°C | 23.21°C | +10.41°C |
| Coefficient of Variation | 13.84% | ~1.34% | **10.3x higher** |

### 2.2 Outlier Analysis

When compared against the baseline established by the four functioning sensors:
- **70.1%** of Sensor 3 readings deviate by more than 2 standard deviations
- **58.2%** of Sensor 3 readings deviate by more than 3 standard deviations
- Maximum deviation from baseline: **11.62°C**

For context, in a normal distribution, only ~5% of readings should exceed 2σ and ~0.3% should exceed 3σ.

### 2.3 Temporal Drift Pattern

Sensor 3 exhibits progressive temperature drift:
- **Days 1-15 average:** 21.96°C (near normal)
- **Days 23-30 average:** 29.37°C (severely elevated)
- **Total drift:** +7.40°C over the monitoring period

The anomaly intensifies over time, with 140 readings exceeding 28°C (all occurring in the latter half of the monitoring period, concentrated in days 23-30).

### 2.4 Comparison with Other Sensors

All other sensors (1, 2, 4, 5) show:
- Consistent mean temperatures around 22.00°C (±0.02°C)
- Low variability (std dev ~0.29-0.31°C)
- Stable readings over time
- Similar error rates (2.36-3.47%)

Sensor 3's error rate (2.78%) is comparable to other sensors, indicating the status flag is **not detecting** the measurement anomalies.

### 2.5 Visual Evidence

See accompanying visualization `sensor_anomaly_analysis.png` which shows:
- **Top-left:** Box plot clearly showing Sensor 3's extreme outliers and elevated distribution
- **Top-right:** Time series revealing progressive temperature escalation in Sensor 3
- **Bottom-left:** Bar chart demonstrating Sensor 3's variability is an order of magnitude higher
- **Bottom-right:** Daily trend showing the accelerating drift pattern

## 3. Recommendations

### Immediate Actions
1. **Decommission Sensor 3** from production monitoring immediately
2. **Discard all Sensor 3 data** from days 23-30 as unreliable
3. **Review data from days 1-22** with caution; early readings appear closer to normal but may already show degradation

### Root Cause Investigation
4. **Physical inspection** of Sensor 3 hardware for:
   - Thermal calibration drift
   - Environmental exposure (direct sunlight, heat source proximity)
   - Component degradation or failure
   - Electrical connection issues

### Preventive Measures
5. **Implement automated anomaly detection** with alerts when:
   - Individual sensor deviates >2°C from peer average
   - Standard deviation exceeds 2x the baseline
   - Progressive drift >0.5°C per day is detected

6. **Establish cross-sensor validation** protocols:
   - Flag sensors when readings consistently diverge from peer group
   - Require manual review when sensor CV exceeds 5%

7. **Replace Sensor 3** with a calibrated unit and monitor closely for the first 7 days

### Data Quality
8. **Retain Sensors 1, 2, 4, and 5** - these show normal, consistent behavior
9. **Use the 4-sensor average** for any critical decisions requiring temperature data from this monitoring period

## Conclusion

Sensor 3 demonstrates clear, statistically significant malfunction characterized by elevated readings, extreme variability (11.4x baseline), and progressive drift (+7.40°C over 30 days). The sensor should be immediately removed from service and replaced.

---
*Analysis Date: 2024*  
*Data Period: June 1-30, 2024*  
*Total Readings Analyzed: 3,600 (720 per sensor)*
