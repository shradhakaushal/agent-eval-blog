# Sensor Anomaly Detection Report

## Executive Summary
Analysis of 30 days of sensor data (720 readings per sensor) has identified **Sensor 3** as malfunctioning. The sensor exhibits severe temperature drift, increasing approximately **0.33°C per day** over the monitoring period, resulting in a total drift of **~10°C** from baseline.

---

## 1. Problematic Sensor Identification

**Sensor 3** is malfunctioning and requires immediate attention.

---

## 2. Evidence Supporting This Conclusion

### 2.1 Temperature Drift
Sensor 3 exhibits a strong linear temperature drift over the 30-day period:
- **Drift rate**: +0.3345°C/day
- **Total drift**: 10.03°C (from ~22°C to ~32°C)
- **Statistical significance**: R² = 0.7357, p-value = 1.12×10⁻²⁰⁹

In contrast, all other sensors show negligible drift:
- Sensor 1: +0.0002°C/day (R² = 0.0000)
- Sensor 2: +0.0003°C/day (R² = 0.0001)
- Sensor 4: -0.0028°C/day (R² = 0.0067)
- Sensor 5: +0.0007°C/day (R² = 0.0005)

### 2.2 Excessive Variability
Sensor 3 shows dramatically higher temperature variability:
- **Standard deviation**: 3.38°C (vs. ~0.29-0.31°C for other sensors)
- **Coefficient of Variation**: 13.84% (vs. ~1.3-1.4% for other sensors)
- **Temperature range**: 19.39°C to 33.62°C (14.23°C span)

Other sensors maintain stable ranges of approximately 1-2°C.

### 2.3 Statistical Outliers
Using a 3-sigma threshold from the overall mean:
- **Sensor 3**: 145 outlier readings (20.1% of all readings)
- **All other sensors**: 0 outlier readings

### 2.4 Humidity Readings Remain Normal
Importantly, Sensor 3's humidity readings are **consistent with other sensors**:
- Mean: 50.24% (overall mean: 50.10%)
- Standard deviation: 5.81% (comparable to other sensors)
- Coefficient of Variation: 11.56% (similar to 11.3-11.7% for others)

This suggests the malfunction is **specific to the temperature sensor component**, not a general sensor failure.

### 2.5 Error Rate
Error rates are comparable across all sensors (2.4-3.5%), indicating that Sensor 3's status reporting mechanism is functioning normally despite the temperature measurement malfunction.

---

## 3. Recommendations

### Immediate Actions (Priority 1)
1. **Remove Sensor 3 from service immediately** - The temperature readings are unreliable and show progressive degradation
2. **Replace the temperature sensing element** - The drift pattern suggests sensor degradation, possibly due to:
   - Thermal calibration drift
   - Component aging
   - Environmental contamination
   - Physical damage to the thermistor/RTD element

### Short-term Actions (Priority 2)
3. **Recalibrate or replace the entire Sensor 3 unit** - Given the severity of drift, replacement is recommended over recalibration
4. **Review historical data** - Determine when the drift began to assess data quality impact
5. **Implement automated drift detection** - Set up alerts for:
   - Temperature drift > 0.1°C/day
   - Standard deviation > 2× normal baseline
   - Readings > 3σ from fleet mean

### Long-term Actions (Priority 3)
6. **Establish preventive maintenance schedule** - Regular calibration checks every 90 days
7. **Implement cross-sensor validation** - Flag sensors that deviate significantly from peer readings
8. **Consider redundant sensors** - Deploy backup sensors in critical monitoring locations

---

## Technical Details

**Analysis Period**: June 1-30, 2024  
**Total Readings**: 3,600 (720 per sensor)  
**Sampling Frequency**: Hourly  
**Sensors Analyzed**: 5 (sensor_1 through sensor_5)  

**Statistical Methods Used**:
- Linear regression analysis for drift detection
- 3-sigma outlier detection
- Coefficient of variation for normalized variability assessment
- Cross-sensor comparative analysis

---

## Appendix: Key Statistics

| Sensor   | Mean Temp (°C) | Std Dev (°C) | CV (%) | Drift (°C/day) | Outliers |
|----------|----------------|--------------|--------|----------------|----------|
| sensor_1 | 22.01          | 0.31         | 1.39   | +0.0002        | 0        |
| sensor_2 | 22.00          | 0.30         | 1.35   | +0.0003        | 0        |
| **sensor_3** | **24.41**  | **3.38**     | **13.84** | **+0.3345** | **145**  |
| sensor_4 | 21.99          | 0.29         | 1.33   | -0.0028        | 0        |
| sensor_5 | 22.02          | 0.29         | 1.31   | +0.0007        | 0        |

---

**Report Generated**: 2024  
**Analyst**: Data Analysis Team  
**Supporting Visualizations**: sensor_anomaly_analysis.png
