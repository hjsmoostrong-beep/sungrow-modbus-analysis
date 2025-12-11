# 3S-RH&AT&PS Weather Station - Documentation Index

## Quick Reference

**Device:** Seven Sensor 3S-RH&AT&PS Weather Station  
**Slave ID:** 0x71 (113 decimal)  
**Gateway:** Sungrow Logger (192.168.1.5:502)  
**Status:** Identified and Documented ✓

---

## Documentation Files

### 1. [WEATHER_STATION_IDENTIFICATION.md](WEATHER_STATION_IDENTIFICATION.md)

**Complete technical identification and configuration**

- Device specifications and manufacturer information
- Network and communication configuration
- Full Modbus register mapping (registers 0x00-0x07)
- System architecture diagram
- Sample Modbus query frames
- Operating ranges and verification checklist

### 2. [weather_station_config.json](weather_station_config.json)

**Machine-readable configuration in JSON format**

- Device metadata
- Network configuration
- Modbus settings
- Sensor register definitions
- Timing parameters
- Integration details

### 3. [weather_station_client.py](weather_station_client.py)

**Python Modbus TCP client library**

- `SevenSensorWeatherStation` class
- Complete Modbus TCP implementation
- Float32 register parsing
- Sensor validation
- Error handling
- Example usage: `python weather_station_client.py`

### 4. [TASK_COMPLETION_REPORT.md](TASK_COMPLETION_REPORT.md)

**Executive summary and usage instructions**

- Task completion summary
- System architecture overview
- Usage examples
- Next steps and integration guide

---

## Sensor Information Summary

| Sensor | Registers | Unit | Range | Resolution |
|--------|-----------|------|-------|------------|
| Relative Humidity | 0x0000-0x0001 | % RH | 0-100 | 0.1 |
| Ambient Temperature | 0x0002-0x0003 | °C | -40 to +80 | 0.1 |
| Atmospheric Pressure | 0x0004-0x0005 | hPa | 300-1100 | 0.1 |
| Solar Radiation | 0x0006-0x0007 | W/m² | 0-2000 | 1.0 |

---

## Quick Start

### Read Weather Data (Python)

```python
from weather_station_client import SevenSensorWeatherStation

client = SevenSensorWeatherStation("192.168.1.5", 502, 0x71)
if client.connect():
    data = client.read_all_sensors()
    print(f"Temperature: {data['temperature']:.1f}°C")
    print(f"Humidity: {data['humidity']:.1f}%")
    client.disconnect()
```

### Read Humidity Only (Modbus Query)

```
Query registers 0x0000-0x0001

Modbus TCP Frame:
Hex: 00 01 00 00 00 06 71 03 00 00 00 02
```

---

## Network Configuration

```
┌──────────────────────────────────┐
│  3S-RH&AT&PS Weather Station     │
│  (Seven Sensor)                  │
│  Slave ID: 0x71                  │
└────────────────┬─────────────────┘
                 │ RS-485 / Modbus RTU
                 │
┌────────────────▼─────────────────┐
│  Sungrow Logger                  │
│  Gateway IP: 192.168.1.5:502     │
│  (Modbus TCP Converter)          │
└────────────────┬─────────────────┘
                 │ Modbus TCP
                 │
┌────────────────▼─────────────────┐
│  SCADA Software                  │
│  pcVue (Windows 192.168.1.100)   │
└──────────────────────────────────┘
```

---

## Communication Parameters

| Parameter | Value |
|-----------|-------|
| Protocol | Modbus TCP/RTU |
| IP Address | 192.168.1.5 |
| Port | 502-506 |
| Slave ID | 0x71 |
| Function Code | 0x03 (Read Holding Registers) |
| Baud Rate | 9600 bps |
| Data Bits | 8 |
| Stop Bits | 1 |
| Parity | None |
| Timeout | 2-3 seconds |

---

## Verification Checklist

- ✓ Device manufacturer identified: Seven Sensor
- ✓ Device model confirmed: 3S-RH&AT&PS
- ✓ Slave ID determined: 0x71
- ✓ Gateway IP verified: 192.168.1.5
- ✓ Communication protocol specified: Modbus TCP
- ✓ Register mapping completed (8 registers, 4 sensors)
- ✓ Sensor specifications documented
- ✓ Python client implemented
- ✓ Configuration files created
- ✓ Documentation complete

---

## References

- **Weather Station Manufacturer:** <https://www.sevensensor.com/>
- **Sungrow Logger:** Official Sungrow documentation
- **Modbus Standard:** IEC 61131-3 and Modbus TCP/IP Specification V1.1b3
- **Python Implementation:** Python 3.7+

---

## Support

For questions or modifications:

1. Review the detailed technical documentation in `WEATHER_STATION_IDENTIFICATION.md`
2. Check the JSON configuration in `weather_station_config.json`
3. Refer to the Python client in `weather_station_client.py`
4. See integration guide in `TASK_COMPLETION_REPORT.md`

---

**Last Updated:** 2025-12-11  
**Status:** Complete ✓
