# Sungrow Integration Quick Reference

## Import
```python
from weather.sungrow_integration import SungrowWeatherReader, ModbusException
```

## Create Reader
```python
reader = SungrowWeatherReader()  # Uses default IP 192.168.1.5:502
```

## Connection
```python
reader.connect()          # Establish connection
reader.is_connected()     # Check status: True/False
reader.disconnect()       # Close connection
```

## Read Data

### Individual Sensors
```python
temp = reader.get_ambient_temperature()        # °C
pv_temp = reader.get_pv_module_temperature()   # °C
irrad = reader.get_irradiance()                # W/m²
wind = reader.get_wind_speed()                 # m/s
```

### All Sensors
```python
data = reader.read_all_sensors()
# Returns: {
#   'ambient_temperature': float,
#   'pv_module_temperature': float,
#   'irradiance': float,
#   'wind_speed': float
# }
```

### By Sensor Key
```python
value = reader.read_sensor_value('ambient_temperature')
# Keys: 'ambient_temperature', 'pv_module_temperature', 
#       'irradiance', 'wind_speed'
```

### With Timestamps
```python
last = reader.get_last_readings()
for key, (value, timestamp) in last.items():
    print(f"{key}: {value} at {timestamp}")
```

## Error Handling
```python
try:
    reader.connect()
    temp = reader.get_ambient_temperature()  # Returns None on error
    irrad = reader.read_sensor_value('irradiance')  # Raises ModbusException
except ModbusException as e:
    print(f"Error: {e}")
finally:
    if reader.is_connected():
        reader.disconnect()
```

## Configuration
```python
reader = SungrowWeatherReader(
    ip_address="192.168.1.5",  # Sungrow Logger IP
    port=502,                  # Modbus TCP port
    slave_id=71,               # Sensor device ID
    timeout=5.0,               # Read timeout (seconds)
    retries=3                  # Retry attempts
)
```

## Complete Example
```python
from weather.sungrow_integration import SungrowWeatherReader

reader = SungrowWeatherReader()

try:
    reader.connect()
    data = reader.read_all_sensors()
    
    for key, value in data.items():
        if value is not None:
            print(f"{key}: {value}")
            
finally:
    reader.disconnect()
```

## Sensor Details

| Sensor | Modbus ID | Register | Type | Coeff | Unit |
|--------|-----------|----------|------|-------|------|
| Ambient Temp | 71 | Holding | U16 | 0.1 | °C |
| PV Temp | 91 | Holding | U16 | 0.1 | °C |
| Irradiance | 85 | Holding | U16 | 1.0 | W/m² |
| Wind Speed | 3 | Input | U16 | 0.1 | m/s |

## Files
- `sungrow_reader.py` - Main client class
- `sensor_definitions.py` - Sensor configurations
- `__init__.py` - Module exports
- `example_usage.py` - Full working example

## Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
# Set to DEBUG for detailed Modbus communication logs
```

---
**Quick Reference** | Sungrow Integration v1.0
