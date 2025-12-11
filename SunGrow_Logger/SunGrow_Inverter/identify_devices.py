#!/usr/bin/env python3
"""
Sungrow Logger Device Identification Tool
Analyzes PCAP capture data to identify all connected devices
"""

import json
from pathlib import Path


class DeviceIdentificationAnalyzer:
    """Analyze captured Modbus data to identify devices"""
    
    def __init__(self, register_map_file):
        """
        Initialize analyzer with register map data
        
        Args:
            register_map_file: Path to sungrow_live_register_map.json
        """
        self.register_map_file = register_map_file
        self.devices = {}
        self.load_register_map()
    
    def load_register_map(self):
        """Load register map from JSON file"""
        try:
            with open(self.register_map_file, 'r') as f:
                data = json.load(f)
                self.metadata = data.get('metadata', {})
                self.registers = data.get('registers_by_unit', {})
        except FileNotFoundError:
            print(f"Error: {self.register_map_file} not found")
            return False
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.register_map_file}")
            return False
        return True
    
    def identify_devices(self):
        """Identify all devices from register map"""
        devices = {
            'inverters': [],
            'weather_station': [],
            'unknown': []
        }
        
        units = self.metadata.get('units', [])
        
        for unit_id in sorted(units):
            device_info = {
                'slave_id': unit_id,
                'slave_id_hex': f'0x{unit_id:02X}',
                'device_type': None,
                'register_count': 0,
                'access_count': 0,
                'function_codes': []
            }
            
            # Get unit data
            unit_key = f'Unit_{unit_id}'
            if unit_key in self.registers:
                unit_data = self.registers[unit_key]
                device_info['register_count'] = len(unit_data.get('registers', {}))
                device_info['function_codes'] = unit_data.get('function_codes', [])
                
                # Identify device type by slave ID and register patterns
                if unit_id in range(1, 7):
                    device_info['device_type'] = 'Sungrow Solar Inverter'
                    devices['inverters'].append(device_info)
                elif unit_id == 247:  # 0xF7
                    device_info['device_type'] = '3S-RH&AT&PS Weather Station (Seven Sensor)'
                    device_info['sensors'] = [
                        'Relative Humidity',
                        'Air Temperature',
                        'Atmospheric Pressure',
                        'Wind Speed',
                        'Solar Irradiance'
                    ]
                    devices['weather_station'].append(device_info)
                else:
                    device_info['device_type'] = 'Unknown Device'
                    devices['unknown'].append(device_info)
            
            # Get access count from metadata
            if 'unit_details' in self.metadata:
                if str(unit_id) in self.metadata['unit_details']:
                    device_info['access_count'] = self.metadata['unit_details'][str(unit_id)].get('access_count', 0)
        
        self.devices = devices
        return devices
    
    def print_summary(self):
        """Print device identification summary"""
        if not self.devices:
            print("No devices identified. Run identify_devices() first.")
            return
        
        print("=" * 90)
        print("SUNGROW LOGGER - DEVICE IDENTIFICATION REPORT")
        print("=" * 90)
        print()
        
        # Summary
        total_devices = len(self.devices['inverters']) + len(self.devices['weather_station'])
        print(f"Total Devices Found: {total_devices}")
        print(f"  - Sungrow Inverters: {len(self.devices['inverters'])}")
        print(f"  - Weather Stations: {len(self.devices['weather_station'])}")
        print(f"  - Unknown Devices: {len(self.devices['unknown'])}")
        print()
        
        # Inverters
        if self.devices['inverters']:
            print("-" * 90)
            print("SUNGROW SOLAR INVERTERS (0x01 to 0x06)")
            print("-" * 90)
            for device in sorted(self.devices['inverters'], key=lambda x: x['slave_id']):
                print(f"\n  Slave ID: {device['slave_id_hex']} ({device['slave_id']} decimal)")
                print(f"  Device: {device['device_type']}")
                print(f"  Registers: {device['register_count']}")
                print(f"  Function Codes: {device['function_codes']}")
        
        # Weather Station
        if self.devices['weather_station']:
            print("\n" + "-" * 90)
            print("WEATHER STATION DEVICES")
            print("-" * 90)
            for device in self.devices['weather_station']:
                print(f"\n  Slave ID: {device['slave_id_hex']} ({device['slave_id']} decimal)")
                print(f"  Device: {device['device_type']}")
                print(f"  Registers: {device['register_count']}")
                print(f"  Function Codes: {device['function_codes']}")
                if 'sensors' in device:
                    print(f"  Sensors:")
                    for sensor in device['sensors']:
                        print(f"    - {sensor}")
        
        # Unknown
        if self.devices['unknown']:
            print("\n" + "-" * 90)
            print("UNKNOWN DEVICES")
            print("-" * 90)
            for device in self.devices['unknown']:
                print(f"\n  Slave ID: {device['slave_id_hex']} ({device['slave_id']} decimal)")
                print(f"  Registers: {device['register_count']}")
                print(f"  Function Codes: {device['function_codes']}")
        
        print("\n" + "=" * 90)
    
    def get_device_summary(self):
        """Return device summary as dictionary"""
        if not self.devices:
            return None
        
        return {
            'total_devices': len(self.devices['inverters']) + len(self.devices['weather_station']),
            'inverters': self.devices['inverters'],
            'weather_stations': self.devices['weather_station'],
            'unknown': self.devices['unknown']
        }


def main():
    """Main execution"""
    
    # Find register map file
    register_map_path = Path('../../data/sungrow_live_register_map.json')
    
    if not register_map_path.exists():
        print(f"Register map not found at {register_map_path}")
        print("Please ensure sungrow_live_register_map.json exists in data/ folder")
        return
    
    # Analyze devices
    print("Analyzing device data...")
    analyzer = DeviceIdentificationAnalyzer(str(register_map_path))
    analyzer.identify_devices()
    analyzer.print_summary()
    
    # Print summary
    summary = analyzer.get_device_summary()
    if summary:
        print("\nDEVICE COUNT BY TYPE:")
        print(f"  Sungrow Inverters: {len(summary['inverters'])}")
        print(f"  Weather Stations: {len(summary['weather_stations'])}")
        print(f"  Unknown Devices: {len(summary['unknown'])}")


if __name__ == '__main__':
    main()

