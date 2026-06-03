# Sensor Anomaly Detection Report

## Executive Summary
Analysis of 30 days of sensor data (720 readings per sensor) has identified **sensor_3** as malfunctioning. This sensor exhibits extreme temperature variability and erratic behavior inconsistent with the other four sensors.

---

## 1. Problematic Sensor Identification

**Sensor: sensor_3**

---

## 2. Evidence Supporting This Conclusion

### 2.1 Temperature Variability
Sensor_3 shows dramatically higher temperature variability compared to all other sensors:

| Metric | sensor_1 | sensor_2 | sensor_3 | sensor_4 | sensor_5 |
|--------|----------|----------|----------|----------|----------|
| **Standard Deviation** | 0.31°C | 0.30°C | **3.38°C** | 0.29°C | 0.29°C |
| **Coefficient of Variation** | 1.39% | 1.35% | **13.84%** | 1.33% | 1.31% |
| **Temperature Range** | 1.97°C | 2.13°C | **14.23°C** | 1.88°C | 1.56°C |

**Key Finding:** Sensor_3's standard deviation (3.38°C) is **more than 10 times higher** than the other sensors (~0.30°C).

### 2.2 Erratic Temperature Readings
Sensor_3 exhibits sudden, large temperature jumps that are physically implausible for a stable environment:

- **Maximum temperature jump:** 3.77°C between consecutive hourly readings
- **Large jumps (>2°C):** 75 occurrences
- **Other sensors:** 0 large jumps each

**Key Finding:** Sensor_3 recorded 75 instances of temperature changes exceeding 2°C between consecutive readings, while all other sensors recorded zero such events.

### 2.3 Temperature Range Anomaly
Sensor_3 recorded temperatures ranging from 19.39°C to 33.62°C, while other sensors remained stable:

- **Sensor_3 range:** 19.39°C - 33.62°C (14.23°C span)
- **Other sensors average range:** ~1.9°C span
- **34% of sensor_3 readings** exceeded 25°C, far above the normal operating range

### 2.4 Statistical Significance
Levene's test for equality of variances confirms that sensor_3's variance is statistically significantly different from other sensors:

- **Test statistic:** 2312.44
- **P-value:** < 0.001 (highly significant)
- **Conclusion:** The probability that sensor_3's variance matches the other sensors is effectively zero

### 2.5 Error Rate Comparison
While sensor_3's error rate (2.78%) is comparable to other sensors (2.36% - 3.47%), the temperature anomalies occur even when the sensor reports "ok" status, indicating the malfunction is not being detected by the sensor's internal diagnostics.

---

## 3. Recommendations

### Immediate Actions
1. **Replace sensor_3 immediately** - The sensor is providing unreliable data that could compromise any decisions based on temperature monitoring
2. **Quarantine existing data** - Mark all sensor_3 readings as unreliable for historical analysis
3. **Investigate root cause** - Examine the physical sensor for:
   - Loose connections causing intermittent readings
   - Thermal cycling or exposure to heat sources
   - Electronic component failure
   - Calibration drift

### Preventive Measures
1. **Implement real-time anomaly detection** - Add automated alerts for:
   - Standard deviation exceeding 1.0°C over any 24-hour period
   - Temperature changes >2°C between consecutive readings
   - Readings outside expected range (e.g., 19-25°C)

2. **Cross-sensor validation** - Flag any sensor reading that deviates >3°C from the median of all sensors at the same timestamp

3. **Enhanced diagnostics** - The current "error" status flag did not detect this malfunction; improve sensor self-diagnostics to include variance checks

4. **Regular calibration** - Establish a calibration schedule to verify sensor accuracy against a known reference

### Data Quality
- **Do not use sensor_3 data** for any temperature-dependent calculations or decisions
- **Recalculate any metrics** that included sensor_3 data using only the four reliable sensors
- Consider the 30-day period as having only 4 functional sensors rather than 5

---

## Supporting Visualizations

See attached files:
- `sensor_analysis.png` - Comprehensive statistical comparison showing temperature distributions, variability, and error rates
- `sensor_timeseries.png` - Time series plots showing sensor_3's erratic behavior over the 30-day period

---

## Conclusion

Sensor_3 is definitively malfunctioning, exhibiting temperature variability more than 10 times higher than its peers, with physically implausible temperature spikes and rapid fluctuations. Immediate replacement is required to maintain data integrity and system reliability.

**Confidence Level:** Very High (p < 0.001)
