# Sungrow Weather Sensor Integration Guide

## Overview

The `sungrow_integration` module provides a complete **Modbus TCP client** for reading real-time weather sensor data from a **Sungrow Logger** connected to a **3S-RH&AT&PS** weather sensor (7-in-1 sensor unit).

**Location:** `src/weather/sungrow_integration/`

## Hardware Configuration

### Sungrow Logger Details
- **IP Address:** 192.168.1.5
- **Port:** 502 (standard Modbus TCP)
- **Slave ID:** 71 (primary sensor device)
- **Connection Type:** Ethernet (Modbus TCP)

### Weather Sensor: 3S-RH&AT&PS
The 7-in-1 sensor measures 4 key environmental parameters:

| Parameter | Modbus ID | Register Type | Data Type | Coefficient | Unit |
|-----------|-----------|---------------|-----------|-------------|------|
| Ambient Temperature | 71 | Holding (0x3) | U16 | 0.1 | °C |
| PV Module Temperature | 91 | Holding (0x3) | U16 | 0.1 | °C |
| Slope Transient Irradiation | 85 | Holding (0x3) | U16 | 1.0 | W/m² |
| Wind Speed | 3 | Input (0x4) | U16 | 0.1 | m/s |

**Coefficient Explanation:**
- Temperature sensors (0.1): Multiply raw register value by 0.1 to get actual temperature
  - Example: Raw value 250 × 0.1 = 25.0°C
- Irradiance (1.0): Use register value directly
- Wind speed (0.1): Multiply raw value by 0.1 to get actual speed
  - Example: Raw value 50 × 0.1 = 5.0 m/s

## Module Structure

### Files

**`__init__.py`** (60 lines)
- Module initialization and exports
- Exposes main API: `SungrowWeatherReader`, `ModbusException`
- Exposes configurations: `SUNGROW_WEATHER_SENSORS`, `SUNGROW_LOGGER_CONFIG`

**`sungrow_reader.py`** (490 lines)
- **SungrowWeatherReader**: Main Modbus TCP client class
- **ModbusException**: Custom exception for Modbus errors
- Features:
  - Automatic connection management
  - Transaction ID generation
  - Modbus request/response packet building and parsing
  - Dual register function support (holding & input registers)
  - Coefficient-based value scaling
  - Sensor data caching with timestamps
  - Comprehensive error handling and logging

**`sensor_definitions.py`** (90 lines)
- **SensorDefinition**: Dataclass for sensor specifications
- **SUNGROW_WEATHER_SENSORS**: Dictionary of 4 configured sensors
- **SUNGROW_LOGGER_CONFIG**: Connection parameters
- **MODBUS_FUNCTION_CODES**: Function code mappings

**`example_usage.py`** (180 lines)
- Complete working example with error handling
- Demonstrates all API methods
- Shows proper connection lifecycle
- Includes formatted output examples

## API Reference

### SungrowWeatherReader Class

#### Constructor
```python
SungrowWeatherReader(
    ip_address: str = "192.168.1.5",
    port: int = 502,
    slave_id: int = 71,
    timeout: float = 5.0,
    retries: int = 3
)
```

#### Connection Management
```python
reader.connect()        # Establish Modbus TCP connection
reader.disconnect()     # Close connection
reader.is_connected()   # Check connection status
```

#### Read Sensor Data
```python
# Read individual sensors
temp = reader.get_ambient_temperature()      # Returns float (°C)
pv_temp = reader.get_pv_module_temperature() # Returns float (°C)
irrad = reader.get_irradiance()              # Returns float (W/m²)
wind = reader.get_wind_speed()               # Returns float (m/s)

# Read all sensors at once
data = reader.read_all_sensors()  # Returns dict with all values

# Read specific sensor by key
value = reader.read_sensor_value('ambient_temperature')

# Get cached readings with timestamps
last = reader.get_last_readings()  # Returns dict of (value, timestamp) tuples
```

#### Error Handling
All read methods raise `ModbusException` on error. Methods with `get_*` prefix return `None` on error instead of raising.

## Usage Examples

### Basic Usage
```python
from weather.sungrow_integration import SungrowWeatherReader

# Create reader instance
reader = SungrowWeatherReader()

try:
    # Connect to Sungrow Logger
    reader.connect()
    
    # Read current values
    ambient_temp = reader.get_ambient_temperature()
    irradiance = reader.get_irradiance()
    wind_speed = reader.get_wind_speed()
    
    print(f"Temperature: {ambient_temp}°C")
    print(f"Irradiance: {irradiance} W/m²")
    print(f"Wind Speed: {wind_speed} m/s")
    
finally:
    reader.disconnect()
```

### Reading All Sensors
```python
reader = SungrowWeatherReader()
reader.connect()

# Get all sensor data in one call
data = reader.read_all_sensors()

for sensor_key, value in data.items():
    if value is not None:
        print(f"{sensor_key}: {value}")
    else:
        print(f"{sensor_key}: READ FAILED")

reader.disconnect()
```

### Error Handling
```python
from weather.sungrow_integration import SungrowWeatherReader, ModbusException

reader = SungrowWeatherReader(ip_address="192.168.1.5")

try:
    reader.connect()
    temp = reader.read_sensor_value('ambient_temperature')
    print(f"Temperature: {temp}°C")
    
except ModbusException as e:
    print(f"Modbus error: {e}")
    
except ConnectionRefusedError:
    print("Cannot connect to Sungrow Logger")
    
finally:
    if reader.is_connected():
        reader.disconnect()
```

### Periodic Data Collection
```python
import time
from weather.sungrow_integration import SungrowWeatherReader

reader = SungrowWeatherReader()
reader.connect()

try:
    while True:
        # Read all sensors
        data = reader.read_all_sensors()
        
        # Get timestamps
        last_reads = reader.get_last_readings()
        
        # Process data
        for key, (value, timestamp) in last_reads.items():
            if value is not None:
                print(f"{key}: {value} at {timestamp}")
        
        # Wait 60 seconds before next read
        time.sleep(60)
        
finally:
    reader.disconnect()
```

## Modbus Protocol Details

### MBAP Header (Modbus Application Protocol)
- Transaction ID: 2 bytes (1-65535)
- Protocol ID: 2 bytes (always 0x0000)
- Length: 2 bytes (PDU + Unit ID)
- Unit ID: 1 byte (slave device ID)

### PDU (Protocol Data Unit)
- Function Code: 1 byte (0x03 or 0x04)
- Starting Address: 2 bytes (register address)
- Quantity: 2 bytes (number of registers)

### Response Format
- MBAP Header: 7 bytes
- Function Code: 1 byte
- Byte Count: 1 byte
- Register Values: N bytes

## Logging

The module uses Python's `logging` module. Enable debug logging to see detailed communication:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
reader = SungrowWeatherReader()
reader.connect()
# Now you'll see detailed Modbus communication logs
```

## Configuration

### Using Custom Connection Parameters
```python
reader = SungrowWeatherReader(
    ip_address="192.168.1.100",  # Different Sungrow Logger IP
    port=502,                     # Standard Modbus TCP port
    slave_id=85,                  # Different sensor device
    timeout=10.0,                 # 10 second timeout
    retries=5                     # 5 retry attempts
)
```

### Default Configuration
Located in `sensor_definitions.py`:
```python
SUNGROW_LOGGER_CONFIG = {
    'ip_address': '192.168.1.5',
    'port': 502,
    'slave_id': 71,
    'timeout': 5.0,
    'retries': 3
}
```

## Integration with Weather Module

### Adding to web_server.py
```python
from weather.sungrow_integration import SungrowWeatherReader

class WeatherServer:
    def __init__(self):
        self.sungrow_reader = SungrowWeatherReader()
        
    def start(self):
        # ... existing code ...
        self.sungrow_reader.connect()
        
    def get_sensor_data(self):
        return self.sungrow_reader.read_all_sensors()
```

### API Endpoint Example
```python
@app.route('/api/sungrow/sensors', methods=['GET'])
def sungrow_sensors():
    try:
        data = sungrow_reader.read_all_sensors()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Troubleshooting

### Connection Refused
**Problem:** `ConnectionRefusedError: [Errno 111]`
- **Cause:** Sungrow Logger not accessible at 192.168.1.5:502
- **Solution:**
  1. Verify Sungrow Logger is powered on
  2. Check IP address with network scanner
  3. Verify network connectivity: `ping 192.168.1.5`
  4. Check firewall rules allow port 502

### Read Timeout
**Problem:** `ModbusException: Read timeout`
- **Cause:** Sungrow Logger not responding within 5 seconds
- **Solution:**
  1. Increase timeout: `SungrowWeatherReader(timeout=10.0)`
  2. Check network latency
  3. Verify sensor is properly connected
  4. Restart Sungrow Logger

### Invalid Register Data
**Problem:** `ModbusException: Invalid register data in response`
- **Cause:** Sensor returns unexpected data format
- **Solution:**
  1. Verify sensor type (3S-RH&AT&PS)
  2. Check Modbus ID configuration
  3. Verify register type (holding vs input)

### Module Import Error
**Problem:** `ModuleNotFoundError: No module named 'weather'`
- **Cause:** Module path not in Python path
- **Solution:**
  1. Run from project root: `cd c:/Users/Public/Videos/modbus/`
  2. Add to path: `import sys; sys.path.insert(0, './src')`
  3. Use as: `from weather.sungrow_integration import SungrowWeatherReader`

## Performance Considerations

- **Connection Overhead:** ~100-200ms per connection
- **Read Time per Sensor:** ~50-100ms (network latency dependent)
- **Read Time All Sensors:** ~200-400ms (4 sequential reads)
- **Cached Data:** Timestamps available for 1+ year

## Future Enhancements

- [ ] Async/await support for non-blocking reads
- [ ] Connection pooling for multiple sensors
- [ ] Data validation and filtering
- [ ] Automatic reconnection on failure
- [ ] Sensor health monitoring
- [ ] Data logging to database
- [ ] Real-time alerts on threshold violations
- [ ] Multiple Sungrow Logger support

## References

- Modbus TCP Standard: RFC 1006
- Sungrow Logger Documentation
- 3S-RH&AT&PS Sensor Specification
- Python Socket Documentation

---

**Module Version:** 1.0.0  
**Last Updated:** 2025-12-11  
**Compatibility:** Python 3.7+  
**Dependencies:** None (uses standard library only)
