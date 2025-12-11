#!/usr/bin/env python3
"""
Weather Station Data Display Utility
Real-time monitoring and logging of 3S-RH&AT&PS sensor data
"""

import time
import json
from datetime import datetime
from pathlib import Path
from weather_station_reader import WeatherStation3S


class WeatherStationMonitor:
    """Monitor and display weather station data"""
    
    def __init__(self, ip: str = "192.168.1.5", port: int = 505,
                 log_file: str = "weather_station_log.json"):
        """
        Initialize monitor
        
        Args:
            ip: Gateway IP
            port: Modbus port
            log_file: File to log readings
        """
        self.client = WeatherStation3S(ip=ip, port=port)
        self.log_file = Path(log_file)
        self.readings_history = []
    
    def display_header(self):
        """Display header"""
        print("\n" + "="*80)
        print("3S-RH&AT&PS WEATHER STATION REAL-TIME MONITOR")
        print("Sungrow Logger: 192.168.1.5:505")
        print("Device: 3S-RH&AT&PS (Seven Sensor)")
        print("="*80)
    
    def display_reading(self, reading_num: int, readings: dict):
        """Display single reading"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[{reading_num}] {timestamp}")
        print("-"*80)
        
        if not readings:
            print("✗ No data available")
            return
        
        # Display each sensor
        for sensor_name, reading in readings.items():
            status_icon = "✓" if reading.status == "OK" else "✗"
            print(f"  {status_icon} {reading.sensor_type:<28} : "
                  f"{reading.value:>8.2f} {reading.unit:<8} "
                  f"(raw: {reading.raw_value})")
    
    def log_readings(self, readings: dict):
        """Log readings to JSON file"""
        try:
            timestamp = datetime.now().isoformat()
            
            log_entry = {
                'timestamp': timestamp,
                'readings': {
                    name: {
                        'value': reading.value,
                        'unit': reading.unit,
                        'raw': reading.raw_value,
                        'type': reading.sensor_type,
                        'status': reading.status
                    }
                    for name, reading in readings.items()
                }
            }
            
            self.readings_history.append(log_entry)
            
            # Write to file
            with open(self.log_file, 'w') as f:
                json.dump(self.readings_history, f, indent=2)
        
        except Exception as e:
            print(f"✗ Logging error: {e}")
    
    def run(self, num_readings: int = 5, interval: int = 2):
        """
        Run monitor
        
        Args:
            num_readings: Number of readings to take
            interval: Seconds between readings
        """
        self.display_header()
        
        if not self.client.connect():
            print("✗ Failed to connect to weather station")
            return
        
        try:
            for i in range(1, num_readings + 1):
                readings = self.client.read_all_sensors()
                self.display_reading(i, readings)
                
                if readings:
                    self.log_readings(readings)
                
                if i < num_readings:
                    print(f"\nWaiting {interval} seconds before next reading...")
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n✗ Interrupted by user")
        
        finally:
            self.client.disconnect()
            print("\n✓ Monitor stopped")


def main():
    """Main execution"""
    
    # Create and run monitor
    monitor = WeatherStationMonitor(
        ip="192.168.1.5",
        port=505,
        log_file="weather_station_log.json"
    )
    
    # Run for 5 readings, 2 seconds apart
    monitor.run(num_readings=5, interval=2)


if __name__ == '__main__':
    main()
