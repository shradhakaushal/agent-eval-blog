# Sensor Anomaly Detection Report

## Executive Summary
**Problematic Sensor Identified: sensor_3**

Sensor 3 exhibits severe calibration drift, with temperature readings increasing by approximately 10°C over the 30-day monitoring period. This represents a critical malfunction requiring immediate attention.

---

## 1. Identified Problematic Sensor

**sensor_3** is malfunctioning and should be taken offline for recalibration or replacement.

---

## 2. Evidence Supporting This Conclusion

### 2.1 Systematic Upward Drift
Sensor 3 shows a clear linear upward drift in temperature readings:
- **Drift rate:** 0.334°C per day (0.0139°C per hour)
- **Total drift:** 10.03°C over 30 days
- **Statistical significance:** R² = 0.736, p-value < 1e-200

In contrast, all other sensors show negligible drift:
- sensor_1: 0.01°C total drift
- sensor_2: 0.01°C total drift
- sensor_4: -0.08°C total drift
- sensor_5: 0.02°C total drift

### 2.2 Abnormal Temperature Statistics
Sensor 3's temperature readings are significantly different from other sensors:

| Metric | sensor_1 | sensor_2 | sensor_3 | sensor_4 | sensor_5 |
|--------|----------|----------|----------|----------|----------|
| Mean (°C) | 22.01 | 22.00 | **24.41** | 21.99 | 22.02 |
| Std Dev (°C) | 0.31 | 0.30 | **3.38** | 0.29 | 0.29 |
| Min (°C) | 20.98 | 21.08 | 19.39 | 21.08 | 21.29 |
| Max (°C) | 22.95 | 23.21 | **33.62** | 22.96 | 22.85 |

Sensor 3's standard deviation is **11× higher** than other sensors, indicating unstable readings.

### 2.3 Excessive Temperature Volatility
Analysis of hour-to-hour temperature changes reveals:

| Sensor | Mean Change (°C) | Max Change (°C) | 95th Percentile (°C) |
|--------|------------------|-----------------|----------------------|
| sensor_1 | 0.36 | 1.46 | 0.86 |
| sensor_2 | 0.32 | 1.60 | 0.82 |
| **sensor_3** | **0.94** | **3.77** | **2.36** |
| sensor_4 | 0.33 | 1.42 | 0.81 |
| sensor_5 | 0.33 | 1.31 | 0.81 |

Sensor 3 shows **2.8× higher** average temperature changes and **2.4× higher** maximum changes.

### 2.4 Progressive Degradation Pattern
Daily average temperatures for sensor_3 show systematic increase:
- Days 1-10: ~22°C (normal range)
- Days 11-20: 22-25°C (beginning drift)
- Days 21-30: 25-32°C (severe drift)

Final readings (Day 30) averaged 31.9°C, compared to ~22°C for all other sensors.

### 2.5 Loss of Correlation
Sensor 3 shows near-zero correlation with other sensors (r = -0.05 to 0.02), while all other sensors also show low correlation with each other, suggesting they are measuring the same stable environment but sensor_3 is not tracking properly.

### 2.6 Error Rate
While error rates are similar across sensors (2.4-3.5%), this metric alone does not distinguish sensor_3's calibration drift issue.

---

## 3. Recommendations

### Immediate Actions (Priority 1)
1. **Take sensor_3 offline immediately** - Current readings are unreliable and drifting rapidly
2. **Investigate root cause** - Likely causes include:
   - Thermal runaway or self-heating issue
   - Calibration circuit failure
   - Environmental contamination (e.g., direct heat source)
   - Sensor element degradation

### Short-term Actions (Priority 2)
3. **Recalibrate or replace sensor_3** - Given the severity of drift (10°C), replacement is recommended over recalibration
4. **Review historical data** - Determine when drift began to assess data validity
5. **Implement drift detection** - Add automated monitoring for:
   - Daily temperature trend analysis
   - Cross-sensor correlation checks
   - Rate-of-change thresholds

### Long-term Actions (Priority 3)
6. **Establish baseline monitoring** - Define acceptable drift rates (e.g., <0.1°C/day)
7. **Implement redundancy** - Use median of multiple sensors rather than individual readings
8. **Schedule preventive maintenance** - Regular calibration checks for all sensors
9. **Add alerting** - Automated alerts when sensor readings deviate >2°C from peer sensors

---

## Supporting Visualizations

See attached files:
- `sensor_analysis.png` - Overview of all sensor readings and distributions
- `sensor_3_drift_analysis.png` - Detailed analysis of sensor_3's drift pattern

---

## Conclusion

Sensor 3 is experiencing severe calibration drift with high statistical confidence (R² = 0.736, p < 1e-200). The 10°C drift over 30 days, combined with 11× higher variability than peer sensors, makes this sensor's data unreliable. Immediate replacement is strongly recommended.

**Data Quality Assessment:**
- Sensors 1, 2, 4, 5: ✓ Operating normally
- Sensor 3: ✗ **FAILED - Requires replacement**

---

*Report generated from analysis of 3,600 sensor readings (720 per sensor) over 30 days*
