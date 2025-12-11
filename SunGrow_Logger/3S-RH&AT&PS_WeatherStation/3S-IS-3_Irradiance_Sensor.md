# 3S-IS-3 Solar Irradiance Sensor (Pyranometer) - Technical Documentation

**Sensor Model:** 3S-IS-3  
**Manufacturer:** Seven Sensor GmbH  
**Category:** Broadband Solar Radiation Pyranometer  
**Standard Classification:** ISO 9060:2018 Secondary Standard  
**Gateway Integration:** 3S-RH&AT&PS Weather Station  
**Modbus Register:** 8085  
**Data Conversion:** Register value / 10 = Solar Irradiance (W/m²)  

---

## Executive Summary

The 3S-IS-3 is a high-precision pyranometer designed for accurate measurement of total solar radiation (direct and diffuse) in photovoltaic installations. It utilizes a thermopile detector with temperature compensation to provide stable measurements across a wide range of environmental conditions and solar angles. The sensor integrates with the Sungrow Logger via Modbus TCP/IP, enabling real-time system efficiency analysis and performance optimization.

---

## Physical Specifications

### Sensor Design

- **Detection Element:** Thermopile (Ni-Cr wire network)
- **Spectral Range:** 300-3000 nm (broadband solar spectrum)
- **Window Material:** Borosilicate glass dome (2mm thickness)
- **Dome Transmittance:** 90%+ in measurement range
- **Housing:** Aluminum with polyester powder coat
- **Leveling:** Bubble level built-in (±2° mounting accuracy)
- **Mounting:** 1/2" NPT thread, universal bracket included
- **Dimensions:** 101mm diameter × 152mm height (with dome)
- **Weight:** 1.2 kg
- **Color:** Black body surface (high emissivity, e = 0.98)

### Environmental Specifications

| Parameter | Value |
|-----------|-------|
| Temperature Range | -40°C to +80°C |
| Operating Humidity | 0-100% RH (non-condensing) |
| Altitude Range | -500m to +3000m |
| Wind Speed Rating | Continuous exposure to 50+ m/s |
| Solar Irradiance Range | 0-1400 W/m² normal; 1400-2000 W/m² with reflections |
| Rain/Snow Resistance | IP66 (dust/water resistant) |
| Hail Resistance | Up to 4cm diameter hailstones |

---

## Measurement Specifications

### Performance Characteristics

| Parameter | Specification |
|-----------|---|
| **Measurement Range** | 0-1400 W/m² (expandable to 2000 W/m²) |
| **Accuracy (% of reading)** | ±5% |
| **Accuracy (absolute)** | ±30 W/m² + reading error |
| **Resolution** | 1 W/m² |
| **Repeatability** | ±2% |
| **Response Time (τ, 95%)** | <5 seconds |
| **Rise Time (0-90%)** | <2 seconds |
| **Sensitivity** | 10 μV per W/m² ±5% |
| **Temperature Coefficient** | <1% per 10°C |
| **Cosine Error** | ±5% (zenith angle 0-60°) |
| **Azimuth Error** | ±2% (azimuth variance 0-360°) |
| **Spectral Error** | <3% (for typical solar spectrum) |

### Calibration Constants

| Parameter | Value |
|---|---|
| **Calibration Factor** | 10.0 μV/(W/m²) |
| **Temperature Coefficient** | -0.15%/°C typical |
| **Stabilization Time** | 30 minutes (after power-up) |
| **Calibration Valid Until** | 3-5 years or 50,000 operating hours |
| **ISO 9060 Classification** | Secondary Standard Pyranometer |

---

## Physical Principles of Operation

### Thermopile Detection

**Thermopile Principle:**

1. **Absorption:** Solar radiation absorbed by black absorber coating
2. **Thermal Generation:** Absorbed energy heats hot junction (thermocouple reference)
3. **EMF Generation:** Temperature difference between hot and cold junctions generates voltage
   - Formula: `V = S × ΔT`
   - Where: S = Seebeck coefficient (~4 μV/K for Ni-Cr), ΔT = temperature difference
4. **Signal Amplification:** Multiple thermocouples in series (stacked) multiply voltage
5. **Conditioning:** Precision electronics convert to 4-20mA or digital output

### Solar Radiation Measurement

**Total Solar Radiation Capture:**

```
Direct Solar Radiation
         ↓
    ┌────●────┐
    │    │    │  ← Borosilicate Dome
    │    ↓    │     (90% transmission)
    │  ┌──┐   │
    │  │▓▓│   │  ← Black Absorber
    │  │▓▓│   │  ← Thermopile Sensor
    │  └──┘   │
    └────┬────┘
         │
      + Diffuse Solar Radiation (sky scattered)
         │
      = Total Global Horizontal Irradiance (GHI)
```

**Wavelength Coverage:**

```
Spectral Response (0-100%)

100% │     ┌─────────────────────┐
     │    ╱                       ╲
 80% │   ╱                         ╲
     │  ╱                           ╲
 60% │ ╱                             ╲
     │╱                               ╲
 40% │                                 ╲
     │                                  ╲
 20% │                                   ╲
     │                                    ╲
  0% └──────────────────────────────────────
     300  500  700  900 1100 1300 1500 1700 nm
     UV  Visible  NIR (Infrared)
     
 Peak Response: 900 nm (near-infrared)
 Width (90%): 300-3000 nm
```

### Temperature Compensation

**Automatic Compensation:**

- Internal temperature sensor monitors thermopile temperature
- Electronics adjust output for temperature drift
- Maintains accuracy across -40°C to +80°C range
- Temperature coefficient: <1% per 10°C

**Compensation Formula:**

```
Irradiance_compensated = (Signal / Sensitivity) × [1 + TC × (T - T_ref)]

Where:
Signal = Raw voltage from thermopile
Sensitivity = 10 μV/(W/m²)
TC = Temperature coefficient (-0.15%/°C)
T = Actual sensor temperature
T_ref = Reference temperature (25°C)
```

---

## Electrical Specifications

### Power Requirements

| Parameter | Value |
|-----------|---|
| **Supply Voltage** | 12V DC or 24V DC (jumper selectable) |
| **Power Consumption** | <1W typical (including conditioning) |
| **Inrush Current** | <200mA |
| **Protection** | Reverse polarity protected |
| **Stabilization** | 30 minutes to full accuracy after power-up |

### Signal Output Specifications

| Parameter | Value |
|---|---|
| **Output Type** | 4-20mA or pulse/digital (model-dependent) |
| **Output Impedance** | <100Ω for current loop |
| **Accuracy** | ±5% of full scale |
| **Response** | Proportional to incident irradiance |
| **Cable Length** | Up to 100m (current loop immune to noise) |
| **Load Resistance** | 200-400Ω typical for 4-20mA |

### Modbus Parameters

| Parameter | Value |
|---|---|
| **Register Address** | 8085 |
| **Data Type** | UINT16 |
| **Scale Factor** | 1/10 |
| **Update Rate** | ~1.45 Hz (Modbus polling) |
| **Unit** | W/m² |
| **Valid Range** | 0-14000 (represents 0-1400 W/m²) |
| **Resolution** | 0.1 W/m² per bit |

---

## ISO 9060:2018 Compliance

### Classification: Secondary Standard Pyranometer

**Specifications:**

- **Directional Error:** ±8% (for zenith angle 0-60°)
- **Temperature Dependency:** ±2% (-10 to +40°C)
- **Response Time:** <5 seconds (95% response)
- **Stabilization:** <5 minutes
- **Accuracy:** ±5% (typical secondary standard)

**vs. Other Classifications:**

| Classification | Accuracy | Response | Directional |
|---|---|---|---|
| **Primary** | ±2% | <2s | ±3% |
| **Secondary** | ±5% | <5s | ±8% |
| **Tertiary** | ±10% | <10s | ±15% |

---

## Installation and Alignment

### Site Selection Requirements

**Optimal Installation Location:**

- Flat, horizontal roof or ground mounting
- Clear sky exposure (270° minimum unobstructed)
- No shading from 8:00 AM to 4:00 PM (±4 hours solar noon)
- Minimum distance from reflective surfaces: 3m
- Avoid proximity to ventilation/exhaust (heat interference)
- Ground or concrete pad preferred (heat absorption uniformity)

**Avoid:**

- Sloped mounting (introduces cosine error)
- Vertical or angled mounting
- Proximity to PV array (heat radiation)
- Dust/dirt accumulation areas
- High temperature zones (air conditioning exhaust)

### Mounting Procedure

**Step-by-Step Installation:**

1. **Prepare Mounting Surface**
   - Select level surface (±2° maximum tilt)
   - Verify structural load capacity (1.2 kg + wind load)
   - Use stainless steel mounting hardware

2. **Level Mounting**
   - Adjust mounting bracket for perfectly horizontal orientation
   - Use built-in bubble level
   - Verify ±2° or better horizontal alignment
   - Check level after installation

3. **Install Sensor**
   - Mount to bracket using 1/2" NPT thread
   - Hand-tighten without over-torque (risk dome damage)
   - Install protective cap when not in use

4. **Orient Correctly**
   - Position for full sky exposure
   - Ensure no shadows on dome at any solar position
   - Verify clear 270° minimum sky view

5. **Cable Routing**
   - Use conduit for cable protection
   - Keep away from power lines
   - Secure with clips every 1-2 meters
   - Use grounding strap if needed

6. **Electrical Connection**
   - Connect 12V or 24V power (verify jumper setting)
   - Connect signal cable to gateway
   - Verify polarity before power-up

7. **Stabilization and Testing**
   - Wait 30 minutes for stabilization
   - Verify reading increases on clear days
   - Compare with reference pyranometer (if available)
   - Log data for 24-hour verification period

### Alignment Verification

**Clear Sky Test:**

```
Time of Day | Expected Irradiance | Tolerance |
08:00       | 200-400 W/m²        | ±10%      |
12:00       | 900-1000 W/m²       | ±5%       |
16:00       | 300-600 W/m²        | ±10%      |
```

---

## Maintenance and Calibration

### Daily Checks

- Inspect dome for dust/dirt accumulation
- Verify no condensation under dome
- Check reading increments in sunlight

### Weekly Maintenance

**Duration:** 10-15 minutes

1. **Dome Cleaning**
   - Gently wipe dome with soft, lint-free cloth
   - Use distilled water or mild isopropyl alcohol (70%)
   - Never use paper towels or abrasive cloths
   - Dry thoroughly with clean cloth

2. **Visual Inspection**
   - Check for dome scratches or cracks
   - Inspect housing for corrosion
   - Verify level mounting (recheck)

### Monthly Maintenance

**Duration:** 30-45 minutes

1. **Deep Cleaning**
   - Remove protective cap
   - Clean dome with compressed air first (removes dust)
   - Use soft brush for stubborn dirt
   - Final wipe with isopropyl alcohol and soft cloth

2. **Optical Check**
   - Look for internal condensation (indicates seal failure)
   - Inspect for insect nests or cobwebs
   - Verify dome clarity (no cloudiness)

3. **Measurement Verification**
   - Compare readings with nearby reference station (if available)
   - Verify response to cloud cover changes
   - Check for dead-band or hysteresis

### Annual Calibration and Service

**Duration:** 1-2 hours

**Professional Service Required:**

1. **Factory Recalibration**
   - Remove sensor from installation
   - Send to manufacturer or certified calibration lab
   - Verify against NIST standard reference
   - Issue calibration certificate with new calibration factor

2. **Physical Inspection**
   - Disassemble dome if possible (manufacturer dependent)
   - Clean interior dome surface
   - Inspect thermopile for damage
   - Replace any corroded components

3. **Electrical Verification**
   - Test sensitivity (should be 10 ±0.5 μV/(W/m²))
   - Verify temperature coefficient (<1%/10°C)
   - Test response time (<5 seconds)

4. **Documentation**
   - Update calibration certificate
   - Record new calibration factor
   - Document any repairs or replacements

### Replacement Criteria

Replace sensor if any of the following occur:

- Dome cracked or severely scratched (optical degradation)
- Internal condensation cannot be resolved (seal failure)
- Measurement accuracy >10% error vs. reference
- Temperature coefficient exceeds ±2%/10°C
- Response time >10 seconds
- Sensitivity drift >10% from factory calibration
- Physical damage to housing or connector

---

## Measurement Examples and Typical Readings

### Daily Irradiance Pattern (Clear Day)

```
Irradiance (W/m²)

1200 │                      ●
     │                    ●   ●
1000 │                  ●       ●
     │                ●           ●
 800 │              ●               ●
     │            ●                   ●
 600 │          ●                       ●
     │        ●                           ●
 400 │      ●                               ●
     │    ●                                   ●
 200 │  ●                                       ●
     │●                                           ●
   0 └──────────────────────────────────────────────
     6   8  10  12  14  16  18  20
     Time of Day (hours)
     
Peak at Solar Noon: ~1000 W/m²
Typical Range: 0-1000 W/m²
```

### Cloudy Day Irradiance Pattern

```
Irradiance (W/m²)

 600 │  ▬▬▭▭▬▬▬▭▭▭▭▬▬▬▬  ▬▬▭▭ 
     │ ▭▭▬▬▬▬▭▭▭▬▬▬▭▭▭▬  ▭▭▬▭
 400 │▬▬▬▭▭▭▬▬▬▭▭▭▭▬▬▬▬▬▭▭▭▬▬
     │▭▭▬▬▬▭▭▭▭▭▬▬▬▭▭▭▬▬▬▭▬▬▬
 200 │▬▬▭▭▬▬▭▭▭▬▬▭▭▭▭▬▬▭▬▬▭▭▬▭
     │▭▬▬▬▭▭▬▬▬▬▬▭▭▬▬▬▭▭▬▬▬▭▭▬
   0 └─────────────────────────
     6   8  10  12  14  16  18  20
     
Peak During Breaks: 300-600 W/m²
Average Range: 50-400 W/m²
Highly Variable (cloud effects)
```

### Irradiance Accuracy Specification

**Error Budget:**

```
Total System Error = ±5% typical

Components:
├─ Calibration Uncertainty: ±1%
├─ Temperature Stability: <1%
├─ Optical Properties: ±2%
├─ Cosine Error (0-60°): ±3% to ±5%
├─ Spectral Sensitivity: <3%
└─ Response Time: <0.5% effect
```

---

## Integration with Solar Systems

### Performance Analysis Applications

**1. Efficiency Calculation**

```
Array Efficiency = (DC Power Output) / (POA Irradiance × Array Area × Module Efficiency)

Example:
- Array Output: 5 kW (5000W)
- Irradiance: 800 W/m²
- Array Area: 25 m²
- Module Efficiency: 18%

Efficiency = 5000 / (800 × 25 × 0.18) = 5000 / 3600 = 139%
(>100% indicates temperature effects; modules run cooler than 25°C STC)
```

**2. Performance Ratio (PR)**

```
PR = Actual Output / Expected Output (at STC)
    = (Actual Efficiency) / (Rated Efficiency at 1000W/m², 25°C)

Target PR: 75-85% (good system)
Acceptable PR: 70-80%
Poor PR: <70% (indicates issues)
```

**3. Temperature-Adjusted Output Prediction**

```
P_actual = P_rated × (G/G_ref) × [1 - TC × (T_mod - T_ref)]

Where:
G = Actual irradiance (from sensor)
G_ref = 1000 W/m² (standard test condition)
T_mod = Module temperature (from PT1000 sensor)
T_ref = 25°C (STC reference)
TC = Temperature coefficient (-0.4% per °C typical)
```

### Forecast and Analysis Applications

**1. Generation Forecasting**

- Short-term (1-4 hours): Cloud cover changes from irradiance trends
- Medium-term (4-24 hours): Weather pattern from irradiance transitions
- Long-term (1-7 days): Seasonal/weather system forecasts

**2. Ramp Rate Analysis**

- Identify rapid irradiance changes
- Predict generation ramps
- Optimize grid integration

**3. Climate Data Collection**

- Solar resource assessment
- Historical weather patterns
- Climate change monitoring

---

## Troubleshooting Guide

### Issue 1: Zero or Consistently Low Readings

**Symptoms:** Reading remains near 0 W/m² even on sunny days

**Diagnosis Steps:**

1. Check for dome obstruction (dirt, snow, ice)
2. Verify horizontal mounting (check bubble level)
3. Ensure no shadows during test hours
4. Check power supply (12/24V present?)
5. Test in full direct sunlight (not shade)

**Solutions:**

- **Dirty Dome:** Clean thoroughly with soft cloth and distilled water
- **Non-Horizontal:** Remount to ensure ±2° horizontal accuracy
- **Shading:** Relocate away from obstructions
- **No Power:** Verify voltage at connector, check power supply
- **Sensor Failure:** Test with known-good cable, consider replacement

### Issue 2: Erratic or Noisy Readings

**Symptoms:** Irradiance jumps wildly, not smooth even on clear days

**Diagnosis Steps:**

1. Check for cloud cover (normal on partly cloudy days)
2. Verify cable shielding and grounding
3. Look for nearby interference sources (radio towers, power lines)
4. Check for loose connectors
5. Monitor over 5-minute period (smooth trends expected)

**Solutions:**

- **Cloudy Conditions:** Expected behavior; reading should average smoothly
- **EMI Interference:** Verify cable shielding grounded at one end only
- **Loose Connection:** Reseat connectors, verify secure fit
- **Cable Damage:** Replace signal cable with shielded twisted pair
- **Electronic Noise:** Verify power supply quality (may need filtering)

### Issue 3: Slow to Respond to Light Changes

**Symptoms:** Reading lags when clouds pass or moving between sun/shade

**Diagnosis Steps:**

1. Verify response time specification (should be <5 seconds)
2. Check for dust/condensation on dome (optical interference)
3. Monitor over extended period (1-2 minutes) for true response time
4. Verify electronics are responding (not a sensor issue)

**Solutions:**

- **Normal Response:** <5 seconds is acceptable; 95% within ~2 seconds
- **Dirty Dome:** Clean and verify improvement
- **Condensation:** Inspect seal, verify no moisture ingress
- **Electronics Issue:** Contact manufacturer for diagnostics

### Issue 4: Consistent Offset from Expected Values

**Symptoms:** Readings consistently 10-20% higher or lower than reference

**Diagnosis Steps:**

1. Compare with nearby reference pyranometer simultaneously
2. Verify mounting level and orientation correct
3. Check calibration date (may be >3 years old)
4. Verify cosine correction appropriate for solar angle

**Solutions:**

- **Calibration Drift:** Send for factory recalibration (3-5 year intervals)
- **Mounting Error:** Verify horizontal within ±2°, clear 270° sky view
- **Systematic Error:** May be normal system difference; verify with reference
- **Sensor Aging:** Consider replacement if calibration unsuccessful

### Issue 5: Dome Damage or Optical Degradation

**Symptoms:** Cloudy/frosted dome, scratches, visible cracks

**Diagnosis Steps:**

1. Inspect dome for moisture (indicates seal failure)
2. Check for internal condensation or dust
3. Test if scratches are on surface (cleanable) or interior (structural damage)
4. Measure accuracy vs. reference (should be <10% error)

**Solutions:**

- **Surface Scratches:** Try gentle polishing with fine lens cleaner
- **Interior Dust:** Cannot be cleaned; may require disassembly (manufacturer)
- **Condensation:** Indicates seal failure; sensor replacement needed
- **Cracks:** Safety/optical issue; replacement recommended

---

## Data Quality Standards

### Valid Measurement Ranges

| Condition | Irradiance Range | Data Quality |
|---|---|---|
| Nighttime | 0-50 W/m² | Valid (twilight) |
| Cloudy | 50-300 W/m² | Valid |
| Partly Cloudy | 300-800 W/m² | Valid |
| Clear Day | 800-1200 W/m² | Valid |
| Peak Summer | 1000-1100 W/m² | Valid peak |
| With Reflections | 1100-1400 W/m² | Valid (rare) |
| Beyond Range | >1400 W/m² | Out of spec (data flagged) |

### Data Filtering Criteria

**Recommended Filtering:**

- Remove readings <10 W/m² (pre-sunrise noise)
- Flag readings >1400 W/m² (beyond specification)
- Apply 1-minute moving average (smooths minor fluctuations)
- Cross-validate with wind speed and temperature (sanity check)

**Quality Flags:**

- GREEN: 50-1400 W/m² under clear sky (high confidence)
- YELLOW: 0-50 W/m² or 1300-1400 W/m² (edge conditions)
- RED: >1400 W/m² or sensor error conditions (investigate)

---

## Specifications Summary Table

| Category | Specification |
|---|---|
| **Measurement** | 0-1400 W/m²; ±5% accuracy; ISO 9060 Secondary |
| **Response** | <5 seconds (95% response) |
| **Temperature** | -40°C to +80°C operating |
| **Mounting** | Horizontal only (±2° level required) |
| **Output** | 4-20mA or pulse; Modbus register 8085 |
| **Calibration** | Every 3-5 years recommended |
| **Maintenance** | Weekly cleaning, monthly inspection |
| **Life Expectancy** | 10-15 years typical; 50,000 operating hours |

---

## References and Standards

- **ISO 9060:2018** - Solar irradiance classification and pyranometer standards
- **WMO Guide** - World Meteorological Organization radiation measurement
- **IEC 61724-1** - Photovoltaic system performance measurement
- **ASTM E824** - Standard test methods for solar irradiance
- **Modbus TCP/IP** - Industrial communication standard
- **Seven Sensor Technical Documentation** - 3S-IS-3 specifications

---

## Support and Warranty

**Manufacturer:** Seven Sensor GmbH  
**Warranty:** 2 years against manufacturing defects  
**Calibration Validity:** 3-5 years (annual verification recommended)  
**Expected Service Life:** 10-15 years

---

## Conclusion

The 3S-IS-3 pyranometer provides accurate, reliable solar irradiance measurement essential for optimizing photovoltaic system performance. Its ISO 9060 Secondary Standard classification ensures compatibility with international solar energy standards while its robust design handles harsh outdoor environments for decades of reliable service. Proper installation, regular maintenance, and periodic recalibration ensure optimal performance throughout the sensor's operational life.
