# Sensor Anomaly Detection Report

## Executive Summary
Analysis of 30 days of sensor data (720 readings per sensor) has identified **Sensor 3** as malfunctioning. The sensor exhibits severe temperature drift, increasing approximately 10°C over the monitoring period, with variance 130 times higher than other sensors.

## 1. Problematic Sensor Identification

**Sensor 3 is malfunctioning.**

## 2. Evidence Supporting This Conclusion

### 2.1 Temperature Drift
Sensor 3 exhibits severe upward drift in temperature readings:
- **Correlation with time**: 0.8578 (extremely high positive correlation)
- **Drift rate**: 0.0139°C per reading
- **Total drift**: ~10.0°C increase over the 30-day period
- **Comparison**: Other sensors show negligible drift (correlation < 0.1, drift < 0.1°C)

### 2.2 Excessive Variability
Sensor 3 shows abnormally high temperature variance:
- **Standard deviation**: 3.38°C (vs. ~0.29°C for other sensors)
- **Coefficient of variation**: 13.8% (vs. ~1.3% for other sensors)
- **Temperature range**: 14.2°C (19.4°C to 33.6°C)
- **Variance ratio**: 130.6× higher than other sensors combined

### 2.3 Statistical Significance
- **T-test**: t-statistic = 37.73, p-value < 1×10⁻²⁶² (highly significant)
- **Mean temperature**: 24.4°C (vs. ~22.0°C for others)
- The difference is not due to random variation

### 2.4 Distribution Analysis
Sensor 3's temperature distribution is bimodal/skewed:
- 34% of readings above 25°C (vs. <1% for other sensors)
- 19% of readings above 28°C
- 11% of readings above 30°C
- Other sensors remain tightly clustered around 22°C ± 0.3°C

### 2.5 Error Rate
Error rates are comparable across all sensors (2.4-3.5%), indicating the malfunction is not flagged by the sensor's internal diagnostics:
- Sensor 1: 2.64%
- Sensor 2: 3.33%
- **Sensor 3: 2.78%**
- Sensor 4: 3.47%
- Sensor 5: 2.36%

### 2.6 Humidity Readings
Humidity readings from Sensor 3 appear normal:
- Mean: 50.2% (consistent with other sensors: 49.9-50.2%)
- Std dev: 5.8% (consistent with other sensors: 5.7-5.8%)
- This suggests the malfunction is specific to the temperature measurement circuit

## 3. Recommendations

### Immediate Actions
1. **Remove Sensor 3 from service immediately** - The drift pattern indicates progressive failure, likely due to:
   - Degraded thermistor or RTD element
   - Failing calibration circuit
   - Thermal runaway in measurement electronics
   
2. **Replace Sensor 3** - The sensor should be replaced, not recalibrated, as the drift pattern suggests hardware degradation

3. **Validate replacement** - After installation, monitor the new sensor for 48-72 hours to ensure stable readings

### Preventive Measures
1. **Implement drift detection** - Add automated monitoring to flag sensors with:
   - Correlation with time > 0.3
   - Standard deviation > 2× the fleet average
   - Drift rate > 0.5°C per week

2. **Cross-sensor validation** - Implement alerts when one sensor deviates >2°C from the fleet median

3. **Calibration schedule** - Establish quarterly calibration checks for all sensors

4. **Root cause analysis** - Investigate Sensor 3 to determine failure mode:
   - Check for environmental factors (excessive heat, moisture, vibration)
   - Review sensor age and maintenance history
   - Consider if other sensors from the same batch/manufacturer are at risk

### Data Quality
- **Historical data from Sensor 3 should be flagged as unreliable** for the entire 30-day period
- If temperature data is critical for this period, interpolate from the four functioning sensors
- The drift appears to start from day 1, suggesting the sensor was already degraded at the beginning of the monitoring period

## Supporting Visualizations
See attached files:
- `sensor_analysis.png` - Overview of all sensor readings and distributions
- `sensor_3_drift_analysis.png` - Detailed analysis of Sensor 3 drift pattern

---
*Report generated from analysis of sensors.csv containing 3,600 total readings (720 per sensor) over 30 days*
