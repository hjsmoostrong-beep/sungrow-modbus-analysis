#!/usr/bin/env python3
"""
Comprehensive Test Suite for 3S-RH&AT&PS Weather Station
Tests all components: reader, monitor, and web server
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
import threading
from weather_station_reader import WeatherStation3S
from weather_station_monitor import WeatherStationMonitor
from weather_station_web import WeatherStationWebServer, WeatherStationWebMonitor


class TestWeatherStationReader:
    """Test the Modbus TCP client"""
    
    @staticmethod
    def test_initialization():
        """Test creating a weather station client"""
        print("\n[TEST] Weather Station Reader - Initialization")
        try:
            station = WeatherStation3S(
                ip='192.168.1.5',
                port=505,
                slave_id=0xF7,
                timeout=5
            )
            assert station.ip == '192.168.1.5'
            assert station.port == 505
            assert station.slave_id == 0xF7
            print("  OK - Client created successfully")
            return True
        except Exception as e:
            print(f"  FAIL - {e}")
            return False
    
    @staticmethod
    def test_connection():
        """Test connecting to the gateway"""
        print("\n[TEST] Weather Station Reader - Connection")
        try:
            station = WeatherStation3S(
                ip='192.168.1.5',
                port=505,
                slave_id=0xF7,
                timeout=5
            )
            if station.connect():
                print(f"  OK - Connected to {station.ip}:{station.port}")
                station.disconnect()
                return True
            else:
                print("  FAIL - Connection unsuccessful")
                return False
        except Exception as e:
            print(f"  FAIL - {e}")
            return False
    
    @staticmethod
    def test_sensor_reading():
        """Test reading all sensors"""
        print("\n[TEST] Weather Station Reader - Sensor Reading")
        try:
            station = WeatherStation3S(
                ip='192.168.1.5',
                port=505,
                slave_id=0xF7,
                timeout=5
            )
            if not station.connect():
                print("  FAIL - Could not connect")
                return False
            
            readings = station.read_all_sensors()
            station.disconnect()
            
            if not readings:
                print("  FAIL - No readings received")
                return False
            
            # Verify all sensors are present
            expected_sensors = ['humidity', 'temperature', 'pressure', 'wind_speed', 'solar_radiation']
            for sensor in expected_sensors:
                if sensor not in readings:
                    print(f"  FAIL - Missing sensor: {sensor}")
                    return False
                reading = readings[sensor]
                print(f"    {sensor:20} : {reading.value:8.2f} {reading.unit}")
            
            print("  OK - All sensors read successfully")
            return True
        except Exception as e:
            print(f"  FAIL - {e}")
            return False


class TestWeatherStationMonitor:
    """Test the monitoring utility"""
    
    @staticmethod
    def test_initialization():
        """Test creating a monitor"""
        print("\n[TEST] Weather Station Monitor - Initialization")
        try:
            monitor = WeatherStationMonitor(
                ip='192.168.1.5',
                port=505
            )
            assert monitor is not None
            print("  OK - Monitor created successfully")
            return True
        except Exception as e:
            print(f"  FAIL - {e}")
            return False
    
    @staticmethod
    def test_single_reading():
        """Test getting a single reading"""
        print("\n[TEST] Weather Station Monitor - Single Reading")
        try:
            monitor = WeatherStationMonitor(
                ip='192.168.1.5',
                port=505
            )
            station = monitor.client
            if station.connect():
                readings = station.read_all_sensors()
                station.disconnect()
                
                if readings:
                    print(f"    Readings retrieved: {len(readings)} sensors")
                    print("  OK - Single reading successful")
                    return True
            print("  FAIL - Could not get reading")
            return False
        except Exception as e:
            print(f"  FAIL - {e}")
            return False


class TestWeatherStationWeb:
    """Test the web server"""
    
    @staticmethod
    def test_web_server_initialization():
        """Test creating a web server"""
        print("\n[TEST] Weather Station Web - Server Initialization")
        try:
            monitor = WeatherStationWebMonitor(
                gateway_ip='192.168.1.5',
                gateway_port=505,
                web_port=8080,
                update_interval=2
            )
            assert monitor.gateway_ip == '192.168.1.5'
            assert monitor.gateway_port == 505
            assert monitor.web_port == 8080
            assert monitor.update_interval == 2
            print("  OK - Web server configured successfully")
            return True
        except Exception as e:
            print(f"  FAIL - {e}")
            return False
    
    @staticmethod
    def test_api_data_structure():
        """Test API data structure"""
        print("\n[TEST] Weather Station Web - API Data Structure")
        try:
            # Check current_data structure
            data = WeatherStationWebServer.current_data
            required_keys = ['humidity', 'temperature', 'pressure', 'wind_speed', 
                           'solar_radiation', 'timestamp', 'status']
            
            for key in required_keys:
                if key not in data:
                    print(f"  FAIL - Missing key: {key}")
                    return False
            
            # Check sensor data structure
            for sensor in ['humidity', 'temperature', 'pressure', 'wind_speed', 'solar_radiation']:
                if 'value' not in data[sensor] or 'unit' not in data[sensor]:
                    print(f"  FAIL - Invalid structure for {sensor}")
                    return False
            
            print("  OK - API data structure valid")
            return True
        except Exception as e:
            print(f"  FAIL - {e}")
            return False


class TestIntegration:
    """Integration tests"""
    
    @staticmethod
    def test_full_workflow():
        """Test complete workflow"""
        print("\n[TEST] Integration - Full Workflow")
        try:
            # Create reader
            station = WeatherStation3S(ip='192.168.1.5', port=505, slave_id=0xF7, timeout=5)
            
            # Connect
            if not station.connect():
                print("  FAIL - Connection failed")
                return False
            
            # Read all sensors
            readings = station.read_all_sensors()
            if not readings:
                print("  FAIL - No sensor data")
                return False
            
            # Verify data format
            for sensor_name, reading in readings.items():
                if reading.value is None or reading.unit is None:
                    print(f"  FAIL - Invalid data for {sensor_name}")
                    station.disconnect()
                    return False
            
            # Disconnect
            station.disconnect()
            
            print(f"  OK - Full workflow successful ({len(readings)} sensors)")
            return True
        except Exception as e:
            print(f"  FAIL - {e}")
            return False


def run_all_tests():
    """Run all test suites"""
    print("=" * 75)
    print("3S-RH&AT&PS WEATHER STATION - COMPREHENSIVE TEST SUITE")
    print("=" * 75)
    
    results = []
    
    # Reader Tests
    print("\n" + "="*75)
    print("WEATHER STATION READER TESTS")
    print("="*75)
    results.append(("Reader Initialization", TestWeatherStationReader.test_initialization()))
    results.append(("Reader Connection", TestWeatherStationReader.test_connection()))
    results.append(("Sensor Reading", TestWeatherStationReader.test_sensor_reading()))
    
    # Monitor Tests
    print("\n" + "="*75)
    print("WEATHER STATION MONITOR TESTS")
    print("="*75)
    results.append(("Monitor Initialization", TestWeatherStationMonitor.test_initialization()))
    results.append(("Monitor Single Reading", TestWeatherStationMonitor.test_single_reading()))
    
    # Web Server Tests
    print("\n" + "="*75)
    print("WEATHER STATION WEB SERVER TESTS")
    print("="*75)
    results.append(("Web Server Init", TestWeatherStationWeb.test_web_server_initialization()))
    results.append(("API Data Structure", TestWeatherStationWeb.test_api_data_structure()))
    
    # Integration Tests
    print("\n" + "="*75)
    print("INTEGRATION TESTS")
    print("="*75)
    results.append(("Full Workflow", TestIntegration.test_full_workflow()))
    
    # Summary
    print("\n" + "="*75)
    print("TEST SUMMARY")
    print("="*75)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status:4}] {test_name}")
    
    print()
    print(f"Total: {passed}/{total} passed ({int(100*passed/total)}%)")
    
    if passed == total:
        print("\n*** ALL TESTS PASSED ***")
    else:
        print(f"\n*** {total-passed} test(s) failed ***")
    
    print("="*75)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
