# Sensor Anomaly Detection Report

## Executive Summary
Analysis of 30 days of sensor data (720 readings per sensor) has identified **Sensor 3** as malfunctioning, exhibiting severe temperature drift that renders its readings unreliable.

---

## 1. Problematic Sensor Identification

**Sensor 3** is experiencing a critical malfunction characterized by progressive temperature drift.

---

## 2. Evidence Supporting This Conclusion

### 2.1 Temperature Drift
- **Sensor 3** shows a systematic upward drift of **+9.90°C** over the 30-day period
  - Day 1 mean: 21.99°C
  - Day 30 mean: 31.88°C
  - Linear drift rate: **0.3348°C/day**

- All other sensors remain stable (changes < 0.14°C):
  - Sensor 1: +0.01°C
  - Sensor 2: -0.03°C
  - Sensor 4: -0.08°C
  - Sensor 5: -0.14°C

### 2.2 Excessive Variability
- **Coefficient of Variation (CV)** analysis reveals Sensor 3's instability:
  - Sensor 3: **13.84%** (10x higher than normal)
  - Sensor 1: 1.39%
  - Sensor 2: 1.35%
  - Sensor 4: 1.33%
  - Sensor 5: 1.31%

- Standard deviation comparison:
  - Sensor 3: **3.38°C** (11x higher than peers)
  - Other sensors: 0.29-0.31°C

### 2.3 Strong Temporal Correlation
- Sensor 3 shows a **0.8578 correlation** between reading number and temperature
- This indicates systematic drift rather than random environmental variation
- Humidity readings remain normal (mean: 50.24%, std: 5.81%), suggesting the issue is specific to the temperature sensor component

### 2.4 Temperature Range Anomaly
- Sensor 3 temperature range: **19.39°C to 33.62°C** (14.23°C span)
- Other sensors range: ~1.8-2.1°C span
- Maximum temperature of 33.62°C is **11.67°C higher** than the next highest reading

### 2.5 Error Rate
- Error rates are comparable across all sensors (2.4-3.5%)
- Sensor 3: 2.78% error rate (20 errors in 720 readings)
- This suggests the drift is not being detected by the sensor's internal diagnostics

---

## 3. Recommendations

### Immediate Actions
1. **Remove Sensor 3 from service immediately** - Current readings are unreliable and show accelerating drift
2. **Quarantine data from Sensor 3** - Mark all readings from this sensor as invalid for analysis
3. **Deploy replacement sensor** - Install a calibrated replacement unit at the Sensor 3 location

### Investigation
4. **Physical inspection** - Examine Sensor 3 for:
   - Thermal contact issues (loose mounting, degraded thermal paste)
   - Component degradation (failing thermistor or RTD)
   - Environmental exposure (direct sunlight, heat source proximity)
   - Electrical issues (power supply instability, ground loops)

### Preventive Measures
5. **Implement drift detection** - Add automated monitoring for:
   - Daily mean temperature trends (alert if >0.1°C/day drift)
   - Coefficient of variation thresholds (alert if CV >3%)
   - Cross-sensor validation (flag outliers >2°C from peer average)

6. **Calibration schedule** - Establish regular calibration checks (monthly recommended)

7. **Redundancy** - Consider deploying backup sensors in critical monitoring locations

---

## Technical Details

**Analysis Period:** June 1-30, 2024  
**Total Readings:** 3,600 (720 per sensor)  
**Sampling Interval:** Hourly  
**Sensors Analyzed:** 5 (sensor_1 through sensor_5)

**Statistical Methods:**
- Descriptive statistics (mean, std, CV)
- Linear regression for drift analysis
- Pearson correlation for temporal patterns
- Z-score analysis for outlier detection

---

## Visualizations

See accompanying files:
- `sensor_analysis.png` - Overview of temperature patterns and distributions
- `sensor_drift_analysis.png` - Detailed drift analysis and temporal trends

---

**Report Generated:** 2024  
**Analyst Recommendation:** CRITICAL - Replace Sensor 3 immediately
