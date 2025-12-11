#!/usr/bin/env python3
"""
3S-RH&AT&PS Weather Station Modbus TCP Client
Reads sensor data from Seven Sensor weather station via Sungrow Logger
Gateway: 192.168.1.5:505
Slave ID: 0xF7 (247)
"""

import socket
import struct
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SensorType(Enum):
    """Sensor types and their register mappings"""
    HUMIDITY = "Humidity"
    TEMPERATURE = "Temperature"
    PRESSURE = "Pressure"
    SOLAR_RADIATION = "Solar_Radiation"
    WIND_SPEED = "Wind_Speed"


@dataclass
class SensorReading:
    """Single sensor reading"""
    sensor_type: str
    value: float
    unit: str
    raw_value: int
    timestamp: float
    status: str = "OK"


class WeatherStation3S:
    """Modbus TCP client for 3S-RH&AT&PS weather station"""
    
    def __init__(self, ip: str = "192.168.1.5", port: int = 505, 
                 slave_id: int = 0xF7, timeout: float = 5.0):
        """
        Initialize weather station client
        
        Args:
            ip: Gateway IP address
            port: Modbus TCP port (505 for this configuration)
            slave_id: Modbus slave ID (0xF7 = 247)
            timeout: Socket timeout in seconds
        """
        self.ip = ip
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.transaction_id = 0
        
        # Register mapping from PCAP analysis
        self.registers = {
            'humidity': (8061, 2),  # 2 registers for Float32
            'temperature': (8063, 2),
            'pressure': (8073, 2),
            'wind_speed': (8082, 1),  # 1 register (UINT16)
            'solar_radiation': (8085, 1),
        }
        
        # Scaling factors
        self.scaling = {
            'humidity': 1.0,  # Raw value interpretation
            'temperature': 1.0,
            'pressure': 0.225,  # ~1013 hPa from raw 4490
            'wind_speed': 0.001,  # raw × 0.001 = m/s
            'solar_radiation': 0.1,  # raw × 0.1 = W/m²
        }
    
    def connect(self) -> bool:
        """
        Connect to Modbus TCP server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip, self.port))
            print(f"[OK] Connected to {self.ip}:{self.port}")
            return True
        except socket.timeout:
            print(f"[ERROR] Connection timeout to {self.ip}:{self.port}")
            return False
        except ConnectionRefusedError:
            print(f"[ERROR] Connection refused by {self.ip}:{self.port}")
            return False
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            print("[OK] Disconnected")
    
    def _build_request(self, start_addr: int, quantity: int) -> bytes:
        """
        Build Modbus TCP request packet
        
        Args:
            start_addr: Starting register address
            quantity: Number of registers to read
            
        Returns:
            Modbus TCP request packet
        """
        self.transaction_id += 1
        
        # Modbus TCP header (7 bytes)
        transaction_id = struct.pack('>H', self.transaction_id)
        protocol_id = struct.pack('>H', 0)  # Modbus protocol
        length = struct.pack('>H', 6)  # Function code + slave + data
        
        # Modbus payload
        function_code = 0x04  # Read Input Registers
        slave_addr = struct.pack('B', self.slave_id)
        start_address = struct.pack('>H', start_addr)
        reg_quantity = struct.pack('>H', quantity)
        
        request = (transaction_id + protocol_id + length + 
                   slave_addr + struct.pack('B', function_code) + 
                   start_address + reg_quantity)
        
        return request
    
    def _parse_response(self, response: bytes) -> Optional[List[int]]:
        """
        Parse Modbus TCP response
        
        Args:
            response: Raw response bytes
            
        Returns:
            List of register values or None if error
        """
        try:
            if len(response) < 9:
                return None
            
            # Check header
            function_code = response[7]
            if function_code & 0x80:  # Error flag
                error_code = response[8]
                print(f"✗ Modbus error: {error_code}")
                return None
            
            byte_count = response[8]
            if len(response) < 9 + byte_count:
                return None
            
            # Extract register values (big-endian UINT16)
            values = []
            for i in range(0, byte_count, 2):
                value = struct.unpack('>H', response[9 + i:9 + i + 2])[0]
                values.append(value)
            
            return values
        except Exception as e:
            print(f"✗ Parse error: {e}")
            return None
    
    def read_registers(self, start_addr: int, quantity: int) -> Optional[List[int]]:
        """
        Read registers from device
        
        Args:
            start_addr: Starting register address
            quantity: Number of registers
            
        Returns:
            List of register values or None if error
        """
        if not self.socket:
            print("✗ Not connected")
            return None
        
        try:
            request = self._build_request(start_addr, quantity)
            self.socket.sendall(request)
            
            response = self.socket.recv(1024)
            if not response:
                print("✗ No response from server")
                return None
            
            return self._parse_response(response)
        except socket.timeout:
            print("✗ Read timeout")
            return None
        except Exception as e:
            print(f"✗ Read error: {e}")
            return None
    
    def read_all_sensors(self) -> Dict[str, SensorReading]:
        """
        Read all sensor values from weather station
        
        Returns:
            Dictionary of sensor readings
        """
        readings = {}
        timestamp = time.time()
        
        try:
            # Read all registers in one operation (8061-8085 = 25 registers)
            values = self.read_registers(8061, 25)
            
            if not values or len(values) < 25:
                print("✗ Failed to read all registers")
                return readings
            
            # Parse individual sensors
            # Register 8061: Humidity (UINT16, 0-65535 = 0-100%)
            humidity_raw = values[0]
            humidity = (humidity_raw / 655.35)  # Scale to 0-100%
            readings['humidity'] = SensorReading(
                sensor_type='Relative Humidity',
                value=round(humidity, 1),
                unit='%',
                raw_value=humidity_raw,
                timestamp=timestamp
            )
            
            # Register 8063: Temperature (UINT16, formula: value/100 - 40)
            temp_raw = values[2]
            temp = (temp_raw / 100.0) - 40  # Convert to °C
            readings['temperature'] = SensorReading(
                sensor_type='Air Temperature',
                value=round(temp, 1),
                unit='°C',
                raw_value=temp_raw,
                timestamp=timestamp
            )
            
            # Register 8073: Pressure (UINT16, formula: 850 + (value * 0.1))
            pressure_raw = values[12]
            pressure = 850 + (pressure_raw * 0.1)  # Scale to hPa
            readings['pressure'] = SensorReading(
                sensor_type='Atmospheric Pressure',
                value=round(pressure, 1),
                unit='hPa',
                raw_value=pressure_raw,
                timestamp=timestamp
            )
            
            # Register 8082: Wind Speed (UINT16, formula: value / 1000)
            wind_speed_raw = values[21]
            wind_speed = wind_speed_raw / 1000.0  # Convert to m/s
            readings['wind_speed'] = SensorReading(
                sensor_type='Wind Speed',
                value=round(wind_speed, 2),
                unit='m/s',
                raw_value=wind_speed_raw,
                timestamp=timestamp
            )
            
            # Register 8085: Solar Radiation/Irradiance (UINT16, formula: value / 10)
            irradiance_raw = values[24]
            irradiance = irradiance_raw / 10.0  # Convert to W/m²
            readings['solar_radiation'] = SensorReading(
                sensor_type='Solar Irradiance',
                value=round(irradiance, 1),
                unit='W/m²',
                raw_value=irradiance_raw,
                timestamp=timestamp
            )
            
            return readings
        
        except Exception as e:
            print(f"✗ Error reading sensors: {e}")
            return readings
    
    def display_readings(self, readings: Dict[str, SensorReading]) -> None:
        """
        Display sensor readings in formatted table
        
        Args:
            readings: Dictionary of sensor readings
        """
        if not readings:
            print("No readings available")
            return
        
        print("\n" + "="*75)
        print("3S-RH&AT&PS WEATHER STATION SENSOR READINGS")
        print("="*75)
        print(f"{'Sensor Type':<25} {'Value':>15} {'Unit':<10} {'Status':<10}")
        print("-"*75)
        
        for key, reading in readings.items():
            print(f"{reading.sensor_type:<25} {reading.value:>15.2f} "
                  f"{reading.unit:<10} {reading.status:<10}")
        
        print("="*75 + "\n")


def main():
    """Main execution"""
    
    # Create client
    client = WeatherStation3S(
        ip="192.168.1.5",
        port=505,
        slave_id=0xF7,
        timeout=5.0
    )
    
    # Try to connect and read data
    if client.connect():
        try:
            # Read all sensors
            readings = client.read_all_sensors()
            
            if readings:
                client.display_readings(readings)
                print("✓ Successfully read sensor data")
            else:
                print("✗ Failed to read sensor data")
        
        finally:
            client.disconnect()
    else:
        print("✗ Failed to connect to weather station")


if __name__ == '__main__':
    main()
