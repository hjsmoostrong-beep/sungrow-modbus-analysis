# Code Quality & Organization Standards

## Project Structure

```
project/
├── src/                          # Source code (organized by functionality)
│   ├── __init__.py              # Package initialization
│   ├── weather/                 # Weather monitoring module
│   │   ├── __init__.py
│   │   ├── station.py           # Weather station data collection
│   │   ├── web_server.py        # Web dashboard and REST API
│   │   └── main.py              # CLI entry point
│   ├── solar/                   # Solar inverter monitoring module
│   │   ├── __init__.py
│   │   ├── sungrow.py           # Sungrow inverter interface
│   │   └── monitor.py           # Solar monitoring logic
│   ├── modbus/                  # Modbus protocol module
│   │   ├── __init__.py
│   │   ├── decoder.py           # Modbus frame decoding
│   │   ├── pipeline.py          # Frame processing pipeline
│   │   ├── analyzer.py          # Live analysis tools
│   │   └── pcap.py              # PCAP file extraction
│   ├── analysis/                # Data analysis tools
│   │   ├── __init__.py
│   │   ├── addresses.py         # Address analysis
│   │   ├── cross_ref.py         # Cross-reference analysis
│   │   └── mapper.py            # Documentation mapping
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── logger.py            # Logging utilities
│       ├── config.py            # Configuration management
│       └── helpers.py           # Common helpers
├── tests/                        # Unit and integration tests
├── data/                         # Data files (JSON, CSV, outputs)
├── docs/                         # Documentation
│   ├── guides/                  # User guides and tutorials
│   └── analysis/                # Technical analysis documents
├── setup.py                      # Package setup
├── requirements.txt              # Dependencies
└── README.md                     # Project overview
```

## Code Style Guidelines

### 1. Import Organization
```python
# Standard library imports (alphabetical)
import json
import struct
import threading
import time
from datetime import datetime
from pathlib import Path

# Third-party imports (if any)
# (alphabetical)

# Local imports
from src.modbus.decoder import ModbusDecoder
from src.utils.logger import Logger
```

### 2. Class Definition Standards
```python
class ClassName:
    """One-line description of class purpose.
    
    Extended description explaining the class functionality,
    important attributes, and typical usage patterns.
    """
    
    def __init__(self, param1: str, param2: int = 10):
        """Initialize the class.
        
        Args:
            param1: Description of param1
            param2: Description of param2 (default: 10)
        """
        self.param1 = param1
        self.param2 = param2
```

### 3. Function Documentation
```python
def function_name(arg1: str, arg2: int) -> dict:
    """One-line description of what the function does.
    
    Extended description with any important notes,
    side effects, or usage patterns.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Dictionary with keys 'status' and 'data'
        
    Raises:
        ValueError: If arg2 is negative
        ConnectionError: If network unavailable
    """
```

### 4. Type Hints
- Always use type hints for function parameters and return types
- Use Optional[Type] for nullable values
- Use List[Type], Dict[Key, Value] from typing module
- Document complex types in docstrings

### 5. Naming Conventions
- **Classes**: PascalCase (ClassName)
- **Functions/Methods**: snake_case (function_name)
- **Constants**: UPPER_SNAKE_CASE (MAX_RETRIES)
- **Private attributes/methods**: Leading underscore (_private_method)
- **Protected attributes/methods**: Single leading underscore (for internal use)

### 6. Code Organization
- Maximum line length: 100 characters
- 2 blank lines between top-level definitions
- 1 blank line between method definitions
- Keep functions under 50 lines when possible
- Keep classes focused on single responsibility

### 7. Error Handling
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    handle_error(e)
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```

### 8. Logging Standards
```python
from src.utils.logger import Logger

logger = Logger(__name__)

# Usage
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical issue")
```

### 9. Constants Definition
```python
# At module level, ABOVE class definitions
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
SENSOR_TYPES = ['bme280', 'dht22', 'anemometer']
```

### 10. JSON/Configuration Files
- Use 2-space indentation
- Use meaningful keys in snake_case
- Include comments explaining complex structures
- Validate structure before use

## Consistency Checklist

- [ ] All imports organized and alphabetical
- [ ] All functions have type hints
- [ ] All classes have docstrings
- [ ] All public methods documented
- [ ] No hardcoded values (use constants)
- [ ] Error handling present
- [ ] Logging statements where appropriate
- [ ] Comments for complex logic
- [ ] Tests written for critical functions
- [ ] No circular imports
- [ ] PEP 8 compliant

## File-Specific Standards

### Weather Module (weather/)
- Sensor data: Use standard units (°C, %, hPa, m/s, mm, lux)
- Thread-safe data access with locks
- Graceful error handling for sensor failures
- JSON serialization for API responses

### Solar Module (solar/)
- Modbus register access with retry logic
- Proper error codes and fault detection
- Energy metrics in standard units (W, kWh, V, A)
- Connection state monitoring

### Modbus Module (modbus/)
- Proper frame validation (CRC checks)
- Comprehensive logging of frame operations
- Support for both RTU and TCP variants
- Proper resource cleanup

### Analysis Module (analysis/)
- Input validation before processing
- Detailed result documentation
- Handling of large datasets efficiently
- JSON output with schema validation

## Testing Standards

- Minimum 80% code coverage
- Unit tests for all utility functions
- Integration tests for module interactions
- Mock external services (Modbus, HTTP)
- Test data fixtures in tests/data/

## Performance Guidelines

- Modbus operations: < 500ms timeout
- API responses: < 100ms
- Data collection cycle: 10 seconds (configurable)
- Memory usage: < 200MB for 24-hour history
- CPU usage: < 5% on Raspberry Pi

## Security Guidelines

- No hardcoded credentials or API keys
- Input validation for all external data
- Safe JSON parsing with error handling
- Proper thread synchronization
- CORS configuration for web API
