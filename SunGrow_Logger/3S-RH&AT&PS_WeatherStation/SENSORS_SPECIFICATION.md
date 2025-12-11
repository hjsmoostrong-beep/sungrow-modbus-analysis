# 3S-RH&AT&PS Weather Station - Connected Sensors Specification

**Station:** 3S-RH&AT&PS (Seven Sensor Weather Station)  
**Gateway:** Sungrow Logger (192.168.1.5:502/505)  
**Integration:** Modbus TCP/IP (Slave ID 0xF7/247)  
**Documentation Date:** December 11, 2025

---

## Overview

The 3S-RH&AT&PS weather station is a comprehensive environmental monitoring device that integrates with Sungrow solar inverters. The station includes five integrated sensors plus three specialized external sensors that provide complete environmental data for:

- Solar irradiance forecasting
- Weather-based system efficiency analysis
- Environmental correlation studies
- Real-time weather conditions

---

## Integrated Sensors (5 Internal)

### 1. Relative Humidity Sensor

**Register:** 8061-8062  
**Range:** 0-100%  
**Accuracy:** ±3%  
**Response Time:** <5 seconds  
**Data Type:** UINT16 normalized  
**Formula:** `humidity = register_8061 / 655.35`

**Purpose:**

- Monitor ambient moisture levels
- Predict dew formation
- Assess weather stability
- Correlate with power output variations

### 2. Air Temperature Sensor

**Register:** 8063-8064  
**Range:** -40°C to +60°C  
**Accuracy:** ±0.5°C  
**Response Time:** <5 seconds  
**Data Type:** UINT16 with offset  
**Formula:** `temperature = (register_8063 / 100) - 40`

**Purpose:**

- Monitor ambient temperature
- Predict inverter derating
- Assess weather patterns
- Correlate with module temperature

### 3. Atmospheric Pressure Sensor

**Register:** 8073-8074  
**Range:** 850-1100 hPa  
**Accuracy:** ±2 hPa  
**Response Time:** <10 seconds  
**Data Type:** UINT16 with offset  
**Formula:** `pressure = 850 + (register_8073 * 0.1)`

**Purpose:**

- Monitor barometric pressure
- Predict weather system movement
- Assess altitude-based performance
- Correlate atmospheric conditions

### 4. Wind Speed Sensor

**Register:** 8082  
**Range:** 0-50+ m/s  
**Accuracy:** ±0.5 m/s  
**Response Time:** <2 seconds  
**Data Type:** UINT16 (cm/s stored)  
**Formula:** `wind_speed = register_8082 / 1000`

**Purpose:**

- Monitor wind conditions
- Predict wind-driven cooling
- Assess weather turbulence
- Correlate with module temperature

### 5. Solar Irradiance Sensor (Pyranometer)

**Register:** 8085  
**Range:** 0-1400 W/m²  
**Accuracy:** ±5%  
**Response Time:** <1 second  
**Data Type:** UINT16 (0.1 W/m² units)  
**Formula:** `irradiance = register_8085 / 10`

**Purpose:**

- Measure incident solar radiation
- Correlate with power output
- Predict system performance
- Assess weather conditions

---

## External Specialized Sensors (3 Connected)

### 1. Wind Speed Sensor: 3S-WS-PLS

**Manufacturer:** Seven Sensor  
**Model:** 3S-WS-PLS  
**Type:** Anemometer (Pulse Output)  
**Integration:** Modbus via 3S-RH&AT&PS Gateway  

#### Specifications

| Parameter | Value |
|-----------|-------|
| **Measurement Range** | 0-50 m/s |
| **Accuracy** | ±0.5 m/s or ±2% (whichever is greater) |
| **Resolution** | 0.1 m/s |
| **Response Time** | <2 seconds |
| **Operating Temperature** | -40°C to +60°C |
| **Operating Humidity** | 0-100% RH |
| **Power Supply** | 12V DC / 24V DC (switchable) |
| **Output** | Pulse output (1 pulse per 0.1 m/s) |
| **Data Transfer** | Modbus TCP via gateway |
| **Register Location** | 8082 (converted to m/s) |

#### Sensor Principle

The 3S-WS-PLS uses a three-cup anemometer design:

- Three hemispherical cups mounted on horizontal arms
- Rotation proportional to wind speed
- Pulse output converted to digital value by gateway
- High reliability in harsh weather conditions

#### Applications

1. **Wind Load Assessment**
   - Monitor wind stress on PV structure
   - Predict wind-induced deflection
   - Assess structural stability

2. **Performance Correlation**
   - Wind chill effect on modules
   - Convective cooling assessment
   - Efficiency optimization

3. **Safety Monitoring**
   - High-wind alarm thresholds
   - System shutdown triggers
   - Weather-based maintenance alerts

#### Maintenance

- Clean cups monthly
- Check bearing alignment quarterly
- Replace cups if deformed
- Verify output pulses annually

---

### 2. Irradiance Sensor: 3S-IS-3

**Manufacturer:** Seven Sensor  
**Model:** 3S-IS-3  
**Type:** Pyranometer (Solar Radiation Sensor)  
**Integration:** Modbus via 3S-RH&AT&PS Gateway  

#### Specifications

| Parameter | Value |
|-----------|-------|
| **Measurement Range** | 0-1400 W/m² |
| **Accuracy** | ±5% |
| **Resolution** | 1 W/m² |
| **Response Time** | <1 second |
| **Operating Temperature** | -40°C to +80°C |
| **Operating Humidity** | 0-100% RH |
| **Spectral Range** | 300-3000 nm (broadband) |
| **Power Supply** | 12V DC / 24V DC |
| **Output** | 4-20 mA (converted to digital) |
| **Data Transfer** | Modbus TCP via gateway |
| **Register Location** | 8085 (in 0.1 W/m² units) |
| **Cosine Correction** | ±5% (typical for solar angle) |
| **Azimuth Sensitivity** | ±5% |

#### Sensor Principle

The 3S-IS-3 is a thermopile pyranometer:

- Silicon photodiode or thermopile detector
- Measures total solar radiation (direct + diffuse)
- Factory calibrated to ISO 9060 standard
- Independent of light spectrum
- Temperature-compensated output

#### Measurement Standards

- **ISO 9060:2018** - Solar radiation classification
- **WMO (World Meteorological Organization)** standards
- **Secondary Standard Pyranometer** equivalent performance

#### Applications

1. **System Performance Monitoring**
   - Real-time efficiency calculation
   - Performance ratio calculation
   - Expected generation forecasting

2. **Power Prediction**
   - Current performance vs. irradiance
   - Peak capacity analysis
   - Seasonal trend analysis

3. **Energy Forecasting**
   - Day-ahead generation prediction
   - Intra-hour ramping analysis
   - Weather impact assessment

#### Data Quality

- **Valid Range:** 50-1400 W/m² (normal operations)
- **Nighttime:** 0-50 W/m² (twilight/reflection)
- **Clear Sky:** 950-1000 W/m² (standard test conditions)
- **Cloudy:** 100-500 W/m² (variable)

#### Maintenance

- Clean protective dome weekly
- Replace protective dome if scratched
- Check mounting alignment monthly
- Verify calibration annually
- Replace if damaged or degraded (>2% drift)

---

### 3. Module Temperature Sensor: 3S-MT-PT1000

**Manufacturer:** Seven Sensor  
**Model:** 3S-MT-PT1000  
**Type:** RTD Temperature Sensor (Pt1000)  
**Integration:** Modbus via 3S-RH&AT&PS Gateway  

#### Specifications

| Parameter | Value |
|-----------|-------|
| **Sensor Type** | Pt1000 (Platinum RTD) |
| **Measurement Range** | -40°C to +100°C |
| **Accuracy** | ±1°C (IEC 60751 Class B) |
| **Resolution** | 0.1°C |
| **Response Time** | <30 seconds |
| **Thermal Time Constant** | 30-50 seconds |
| **Operating Voltage** | 12V DC / 24V DC |
| **Power Consumption** | <1W |
| **Resistance Ratio** | R(0°C) = 1000Ω |
| **Temperature Coefficient** | ±0.385 Ω/°C |
| **Output** | 4-20 mA or digital |
| **Data Transfer** | Modbus TCP via gateway |
| **Register Location** | 8063-8064 (ambient) or dedicated registers |
| **Housing** | Stainless steel probe (IP67) |
| **Cable Length** | Typically 2-5 meters (configurable) |

#### RTD Principle

The Pt1000 is a Platinum Resistance Temperature Detector:

- Pure platinum wire coil encapsulated in ceramic
- Resistance increases linearly with temperature
- 2-wire or 3-wire connection for accuracy
- International IEC 60751 standard
- Factory calibrated at 0°C and 100°C

#### Resistance vs Temperature

```
R(T) = R0 × [1 + A×T + B×T² (for T < 0°C)]
R(T) = R0 × [1 + A×T]        (for T ≥ 0°C)

Where:
R0 = 1000Ω @ 0°C
A = 3.9083 × 10⁻³ °C⁻¹
B = -5.775 × 10⁻⁷ °C⁻²
```

#### Applications

1. **PV Module Temperature Monitoring**
   - Direct module temperature measurement
   - Performance deration calculation
   - Thermal stress assessment
   - Safety shutdown triggers

2. **Efficiency Correlation**
   - Temperature coefficient analysis
   - System derating prediction
   - Ambient vs. module comparison
   - Thermal loss calculation

3. **Predictive Maintenance**
   - Detect abnormal temperature rise
   - Identify shading or faults
   - Monitor aging effects
   - Verify cooling performance

#### Temperature Measurement Modes

- **Ambient Temperature:** Sensor in shaded location
- **Module Temperature:** Sensor in direct contact with PV module
- **Irradiance Correlation:** Combined with solar radiation data
- **Efficiency Reference:** Standard test condition comparison

#### Typical Values

```
Ambient: 25°C    → Resistance: ~1096.3Ω
Module:  45°C    → Resistance: ~1177.5Ω
Hot Day: 60°C    → Resistance: ~1232.8Ω
Cold Day: 0°C    → Resistance: ~1000.0Ω
```

#### Maintenance

- Check probe contact integrity monthly
- Verify cable insulation annually
- Clean probe from dirt/corrosion
- Ensure secure mounting on module
- Replace if thermal time constant changes >10%

---

## Modbus Register Integration

### Complete Register Mapping with Sensors

| Register | Sensor | Parameter | Units | Formula | Range |
|----------|--------|-----------|-------|---------|-------|
| 8061-8062 | Internal | Humidity | % | `/655.35` | 0-100 |
| 8063-8064 | 3S-MT-PT1000 | Temperature | °C | `/100 - 40` | -40 to +60 |
| 8073-8074 | Internal | Pressure | hPa | `850 + (*0.1)` | 850-1100 |
| 8082 | 3S-WS-PLS | Wind Speed | m/s | `/1000` | 0-50+ |
| 8085 | 3S-IS-3 | Solar Irradiance | W/m² | `/10` | 0-1400 |

### Data Update Rates

| Sensor | Update Interval | Samples/Second | Modbus Frequency |
|--------|---|---|---|
| Humidity (internal) | 5 seconds | 0.2 | 1.45 Hz overall |
| Temperature (Pt1000) | 30 seconds | 0.033 | Continuous polling |
| Pressure (internal) | 10 seconds | 0.1 | 1.45 Hz overall |
| Wind Speed (3S-WS-PLS) | 2 seconds | 0.5 | Continuous polling |
| Solar Irradiance (3S-IS-3) | 1 second | 1.0 | Continuous polling |

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│         3S-RH&AT&PS Weather Station             │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─ INTEGRATED SENSORS (5) ──────┐            │
│  │ • Humidity Sensor (%)           │            │
│  │ • Air Temperature (-40 to +60°C)│            │
│  │ • Pressure (850-1100 hPa)       │            │
│  │ • Wind Speed (0-50+ m/s)        │            │
│  │ • Solar Irradiance (0-1400 W/m²)│            │
│  └─────────────────────────────────┘            │
│                                                 │
│  ┌─ CONNECTED EXTERNAL SENSORS (3) ─┐         │
│  │ • 3S-WS-PLS (Wind Anemometer)     │         │
│  │ • 3S-IS-3 (Pyranometer)           │         │
│  │ • 3S-MT-PT1000 (Temp RTD)         │         │
│  └───────────────────────────────────┘         │
│                                                 │
│  ┌─ GATEWAY PROCESSING ──────────────────┐    │
│  │ • 25 Input Registers (8061-8085)      │    │
│  │ • Real-time data conversion           │    │
│  │ • Modbus TCP/IP encapsulation        │    │
│  │ • Polling: ~1.45 Hz                   │    │
│  └───────────────────────────────────────┘    │
│                                                 │
└──────────────┬──────────────────────────────────┘
               │ Modbus TCP/IP
               │ Slave ID: 0xF7 (247)
               │ Function Code: 4
               │
         ┌─────▼──────────────┐
         │ Sungrow Logger     │
         │ (192.168.1.5:502)  │
         │                    │
         │ Port 505 (alt)     │
         └─────┬──────────────┘
               │
         ┌─────▼──────────────┐
         │ PCVUE SCADA        │
         │ (192.168.1.100)    │
         └────────────────────┘
```

---

## Performance Specifications

### Measurement Accuracy Summary

| Parameter | Accuracy | Resolution | Response Time |
|-----------|----------|------------|---|
| Humidity | ±3% | 1% | <5 sec |
| Temperature | ±0.5°C / ±1°C | 0.1°C | <30 sec |
| Pressure | ±2 hPa | 0.1 hPa | <10 sec |
| Wind Speed | ±0.5 m/s | 0.1 m/s | <2 sec |
| Solar Irradiance | ±5% | 1 W/m² | <1 sec |

### Environmental Limits

| Parameter | Range |
|-----------|-------|
| Operating Temperature | -40°C to +80°C |
| Operating Humidity | 0-100% RH (non-condensing) |
| Pressure Range | 700-1100 hPa (altitude -500m to +3000m) |
| Maximum Wind Speed | 50+ m/s |
| Maximum Solar Irradiance | 1400+ W/m² (with reflections) |

---

## Calibration and Maintenance

### Annual Maintenance Checklist

- [ ] **Wind Sensor (3S-WS-PLS)**
  - [ ] Clean anemometer cups
  - [ ] Check bearing rotation (smooth, no friction)
  - [ ] Verify output pulse consistency
  - [ ] Inspect structural mounting

- [ ] **Irradiance Sensor (3S-IS-3)**
  - [ ] Clean protective dome (with soft cloth, alcohol)
  - [ ] Inspect dome for scratches or cracks
  - [ ] Verify level mounting (within ±5°)
  - [ ] Check cable integrity
  - [ ] Calibration check against reference (optional)

- [ ] **Temperature Sensor (3S-MT-PT1000)**
  - [ ] Verify probe contact with module
  - [ ] Check cable insulation
  - [ ] Clean probe from corrosion
  - [ ] Thermal response test

- [ ] **Overall System**
  - [ ] Verify all register values within expected range
  - [ ] Check Modbus communication latency
  - [ ] Verify data logging continuity
  - [ ] Update firmware if available

### Troubleshooting

**Issue:** Humidity readings always 0%

- Solution: Check register 8061 connectivity, verify sensor power supply

**Issue:** Wind speed erratic**

- Solution: Clean anemometer cups, check bearing, verify connection

**Issue:** Temperature offset from expected

- Solution: Verify probe contact, check calibration, clean probe

**Issue:** Solar irradiance reads low on clear days

- Solution: Clean dome, check sensor level, verify no shading

---

## Integration with Solar System

### Efficiency Analysis

The combination of these sensors enables:

1. **Real-time Efficiency Calculation**
   - `Efficiency = Actual Output / (Irradiance × Area × Module Efficiency)`

2. **Temperature Derating**
   - `Derating = 1 - TCp × (Tmodule - Tstd)`
   - Where TCp = temperature coefficient (-0.4% to -0.5% per °C typical)

3. **Weather Correlation**
   - Wind speed effect on cooling
   - Cloud cover (from irradiance variation)
   - Dew formation risk (humidity + temperature)

4. **Performance Forecasting**
   - Predict output based on weather conditions
   - Day-ahead generation estimates
   - 5-minute ramping analysis

---

## References and Standards

- **ISO 9060:2018** - Solar radiation measurement classification
- **IEC 61721-1** - Photovoltaic systems - Acceptance test procedures
- **IEC 60751** - Industrial platinum resistance thermometers
- **WMO Guide** - World Meteorological Organization measurement standards
- **Modbus TCP/IP** - Industrial automation protocol
- **Seven Sensor Technical Documentation** - 3S-RH&AT&PS specifications

---

## Conclusion

The 3S-RH&AT&PS weather station with its three connected specialized sensors (3S-WS-PLS, 3S-IS-3, 3S-MT-PT1000) provides comprehensive environmental monitoring for solar photovoltaic installations. This integration enables:

✅ Real-time environmental tracking  
✅ System performance correlation  
✅ Predictive maintenance  
✅ Weather-based optimization  
✅ Data-driven decision making  

All sensor data is accessible via Modbus TCP/IP and integrated seamlessly with the Sungrow Logger and PCVUE SCADA system.
