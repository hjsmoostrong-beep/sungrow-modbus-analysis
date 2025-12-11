# MANUAL VERIFICATION REPORT - Address, Type, and Coefficient Check

**Date:** December 11, 2025  
**Source:** PDF Manuals

- `Setting_Instructions_for_Sungrow_Weather_Station.pdf` (Primary)
- `3S-Sensor_Box.pdf` (Secondary)

---

## Executive Summary

**CRITICAL ISSUES FOUND:**

The current documentation contains INCORRECT register addresses, data types, and coefficients compared to the official Sungrow/Seven Sensor manuals. The discrepancies affect ALL sensor measurements:

❌ **Current:** Registers 8061-8085 (Sungrow Logger format)
✅ **Manual:** Registers 3, 12, 15, 21, 29, 33, 52, 53 (Seven Sensor format)

**Impact:** Current coefficient calculations will produce WRONG sensor readings!

---

## Manual Specification Table

### From Setting_Instructions_for_Sungrow_Weather_Station.pdf

**Modbus RTU Specifications:**

- Supported Bus Protocol: MODBUS RTU
- Baud Rate: 3800, 9600, 19200, 38400
- Parity: None, Even, Odd
- Stop Bit: 1, 2 (only at no parity)
- Factory Default: 9600 Baud, 8N1, Address: 1
- Supported Function Code: 0x04 (Read Input Register)

### Register Map (Official from Manual)

| ID-Dec | ID-Hex | Parameter | Data Type | Range | Unit | Scale |
|--------|--------|-----------|-----------|-------|------|-------|
| 3 | 0x03 | Wind Speed | US | 0...6000 | 1/100 m/s | ÷100 |
| 12 | 0x0C | Irradiance (Temp Compensated) | US | 0...1600 | 0.1 W/m² | ÷10 |
| 15 | 0x0F | Cell Temperature | S | -400...+850 | 0.1°C | ÷10 |
| 21 | 0x1D | External Temperature 1 | S | -400...+850 | 0.1°C | ÷10 |
| 29 | 0x15 | External Temperature 2 | S | -400...+850 | 0.1°C | ÷10 |
| 33 | 0x21 | Relative Humidity | US | 0...100 | 1% | ÷1 |
| 52 | 0x34 | Wind Direction | US | 0...359 | 1° | ÷1 |
| 53 | 0x35 | Wind Speed (Alt) | US | 0...6000 | 1/100 m/s | ÷100 |

**Notes from Manual:**

- *Register addresses can be different as per software version of the sensor*
- Data Type: S = Signed, US = Unsigned Short
- Software version: 8 and newer

---

## Current Documentation vs. Manual

### MISMATCH 1: Wind Speed Sensor

**Current Documentation:**

```
Register: 8082
Formula: register_8082 / 1000 = Wind Speed (m/s)
Range: 0-50+ m/s
```

**Manual Specification:**

```
Register: 53 (0x35) OR 3 (0x03)
Formula: register_value / 100 = Wind Speed (m/s)
Range: 0-6000 (= 0-60 m/s when divided by 100)
Data Type: US (Unsigned Short)
```

**Issue:**

- ❌ Register address WRONG (8082 vs 53)
- ❌ Coefficient WRONG (÷1000 vs ÷100)
- ✅ Range roughly correct but basis is different

**CORRECTION:** Wind Speed = register_53 / 100 (or register_3 / 100)

---

### MISMATCH 2: Solar Irradiance Sensor

**Current Documentation:**

```
Register: 8085
Formula: register_8085 / 10 = Solar Irradiance (W/m²)
Range: 0-1400 W/m²
Data Type: UINT16 (0.1 W/m² units)
```

**Manual Specification:**

```
Register: 12 (0x0C)
Formula: register_value / 10 = Irradiance (W/m²)
Range: 0-1600 (= 0-160 W/m² when divided by 10) OR (= 0-160 when units are 0.1 W/m²)
Data Type: US (Unsigned Short)
Parameter: Temperature Compensated Irradiance
```

**Issue:**

- ❌ Register address WRONG (8085 vs 12)
- ✅ Coefficient CORRECT (÷10)
- ⚠️ Range different (1400 vs 1600 raw value, or 140 vs 160 W/m² at 0.1 scale)

**CORRECTION:** Irradiance = register_12 / 10 (SAME FORMULA BUT DIFFERENT REGISTER!)

---

### MISMATCH 3: Temperature Sensor (Cell/Module)

**Current Documentation:**

```
Register: 8063-8064
Formula: (register_8063 / 100) - 40 = Temperature (°C)
Range: -40°C to +616°C
Data Type: UINT16 with offset
```

**Manual Specification:**

```
Register: 15 (0x0F)
Formula: register_value / 10 = Temperature (°C)
Range: -400 to +850 (= -40°C to +85°C when divided by 10)
Data Type: S (Signed short)
Parameter: Cell Temperature
```

**Issue:**

- ❌ Register address WRONG (8063 vs 15)
- ❌ Coefficient COMPLETELY WRONG ((÷100) - 40 vs ÷10)
- ❌ Data Type WRONG (UINT16 vs Signed)
- ❌ Range WRONG (0 to +616°C vs -40°C to +85°C)

**CORRECTION:** Temperature = register_15 / 10 (SIGNED VALUE!)

**Example:**

```
Manual value -400 → -400 / 10 = -40°C ✓
Manual value 0 → 0 / 10 = 0°C ✓
Manual value 250 → 250 / 10 = 25°C ✓
Manual value 850 → 850 / 10 = 85°C ✓

Current (WRONG) formula with value 250:
(250 / 100) - 40 = 2.5 - 40 = -37.5°C ❌ WRONG!
```

---

### MISMATCH 4: External Temperature 1 (Ambient)

**Current Documentation:**

```
Register: Not separately identified
Assumed part of 8063-8064
```

**Manual Specification:**

```
Register: 21 (0x1D)
Formula: register_value / 10 = Temperature (°C)
Range: -400 to +850 (= -40°C to +85°C)
Data Type: S (Signed short)
Parameter: External Temperature 1
```

**Issue:**

- ❌ Register address NOT IDENTIFIED in current documentation
- ❌ Coefficient DIFFERENT

**CORRECTION:** Add separate External Temperature 1 = register_21 / 10

---

### MISMATCH 5: External Temperature 2

**Current Documentation:**

```
Register: Not separately identified
```

**Manual Specification:**

```
Register: 29 (0x15)
Formula: register_value / 10 = Temperature (°C)
Range: -400 to +850 (= -40°C to +85°C)
Data Type: S (Signed short)
Parameter: External Temperature 2
```

**Issue:**

- ❌ Not documented in current implementation

**CORRECTION:** Add External Temperature 2 = register_29 / 10

---

### MISMATCH 6: Relative Humidity

**Current Documentation:**

```
Register: 8061-8062
Formula: register_8061 / 655.35 = Humidity (%)
Range: 0-100%
Data Type: UINT16 normalized
```

**Manual Specification:**

```
Register: 33 (0x21)
Formula: register_value / 1 = Humidity (%)
Range: 0-100 (1% resolution)
Data Type: US (Unsigned Short)
Parameter: Relative Humidity
```

**Issue:**

- ❌ Register address WRONG (8061 vs 33)
- ❌ Coefficient COMPLETELY WRONG (÷655.35 vs ÷1)
- ⚠️ Range is same but achieved differently

**CORRECTION:** Humidity = register_33 / 1 (or just register_33 value)

**Example:**

```
Manual value 75 → 75 / 1 = 75% ✓

Current (WRONG) formula with value 49500:
49500 / 655.35 = 75.5% 

BUT manual would store 75 directly!
Current formula expects 0-65535 range mapped to 0-100%
Manual expects 0-100 directly
```

---

### MISMATCH 7: Wind Direction

**Current Documentation:**

```
Register: Not identified
Not currently implemented
```

**Manual Specification:**

```
Register: 52 (0x34)
Formula: register_value / 1 = Wind Direction (°)
Range: 0-359 (1° resolution)
Data Type: US (Unsigned Short)
Parameter: Wind Direction
```

**Issue:**

- ❌ Not implemented in current documentation

**CORRECTION:** Add Wind Direction = register_52 / 1

---

## Atmospheric Pressure

**Current Documentation:**

```
Register: 8073-8074
Formula: pressure = 850 + (register_8073 * 0.1)
```

**Manual Specification:**

```
Not found in manual register map!
```

**Issue:**

- ⚠️ Pressure NOT LISTED in official Sungrow/Seven Sensor manual
- This may be an extension or the manual may be incomplete

**Status:** CANNOT VERIFY - May need to contact manufacturer

---

## Summary of Corrections Required

### Register Mapping Corrections

| Sensor | Current Reg | Manual Reg | Current Formula | Manual Formula | Status |
|--------|-------------|-----------|-----------------|---|---|
| **Wind Speed** | 8082 | 3 or 53 | ÷1000 | ÷100 | ❌ WRONG |
| **Irradiance** | 8085 | 12 | ÷10 | ÷10 | ⚠️ Register wrong |
| **Cell Temp** | 8063 | 15 | (÷100)-40 | ÷10 (signed) | ❌ WRONG |
| **Ext Temp 1** | N/A | 21 | N/A | ÷10 (signed) | ❌ MISSING |
| **Ext Temp 2** | N/A | 29 | N/A | ÷10 (signed) | ❌ MISSING |
| **Humidity** | 8061 | 33 | ÷655.35 | ÷1 | ❌ WRONG |
| **Wind Dir** | N/A | 52 | N/A | ÷1 | ❌ MISSING |
| **Pressure** | 8073 | N/A | 850+(*0.1) | N/A | ⚠️ NOT IN MANUAL |

---

## Impact Analysis

### Current Implementation Issues

1. **Wind Speed: 10x ERROR**
   - Current: ÷1000 (coefficient 0.001)
   - Manual: ÷100 (coefficient 0.01)
   - **Impact:** All wind readings 10x TOO SMALL
   - Example: 6000 register → 6 m/s (current) vs 60 m/s (correct)

2. **Temperature: SEVERE ERROR**
   - Current: (÷100) - 40 = formula for -40°C offset range
   - Manual: ÷10 on signed value
   - **Impact:** Temperatures completely wrong, possibly negative when should be positive
   - Example: 250 register → -37.5°C (current/WRONG) vs 25°C (correct)

3. **Humidity: 655x ERROR**
   - Current: ÷655.35 (mapping 0-65535 to 0-100)
   - Manual: ÷1 (direct value 0-100)
   - **Impact:** If manual sends 75, current code divides by 655.35 = 0.11% (VERY WRONG)

4. **Irradiance: REGISTER ERROR (but formula OK)**
   - Current: Register 8085 ÷10
   - Manual: Register 12 ÷10
   - **Impact:** May be reading from wrong register entirely

---

## Recommendations

### IMMEDIATE ACTIONS

1. **Verify Register Addresses**
   - Determine if current system uses Registers 8061-8085 (Sungrow extended) or registers 3,12,15,21,29,33,52,53 (Seven Sensor)
   - Check Sungrow Logger documentation for any register mapping extensions

2. **Correct Coefficients**
   - Wind: Change from ÷1000 to ÷100
   - Temperature: Change from (÷100)-40 to ÷10
   - Humidity: Change from ÷655.35 to ÷1

3. **Fix Data Types**
   - Temperature values should be read as SIGNED (not unsigned)
   - Allows negative temperatures

4. **Add Missing Sensors**
   - External Temperature 1 (Register 21)
   - External Temperature 2 (Register 29)
   - Wind Direction (Register 52)

### VERIFICATION STEPS

1. Read manual register values with oscilloscope or Modbus sniffer
2. Compare against current readings
3. Apply corrections and validate
4. Test with known temperature/humidity/wind conditions

---

## Files Requiring Updates

Based on manual specifications, the following documentation files need correction:

1. **SENSORS_SPECIFICATION.md**
   - Update register mapping table
   - Correct all coefficients
   - Update data types

2. **3S-WS-PLS_Wind_Speed_Sensor.md**
   - Change coefficient from ÷1000 to ÷100

3. **3S-IS-3_Irradiance_Sensor.md**
   - Change register from 8085 to 12

4. **3S-MT-PT1000_Temperature_Sensor.md**
   - Change register from 8063 to 15
   - Change formula from (÷100)-40 to ÷10
   - Change data type from UINT16 to Signed

5. **weather_station_reader.py** (Python code)
   - Update all coefficients and register addresses
   - Change temperature parsing to signed integer

---

## Next Steps

1. ✅ Review manual specifications (DONE)
2. ⏳ Verify which register set is actually being used (TODO)
3. ⏳ Correct Python code with proper registers and coefficients (TODO)
4. ⏳ Update all documentation files (TODO)
5. ⏳ Test with real sensor data and validate corrections (TODO)
6. ⏳ Update PCAP analysis with correct coefficients (TODO)

---

## Conclusion

The current sensor documentation contains significant errors in register addresses and coefficient calculations. The manual specifications from Seven Sensor and Sungrow show that MOST current values are INCORRECT. Urgent correction required for accurate sensor measurements.
