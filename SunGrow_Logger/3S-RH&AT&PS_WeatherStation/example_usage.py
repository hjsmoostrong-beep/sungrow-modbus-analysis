#!/usr/bin/env python3
"""
Example Usage: 3S-RH&AT&PS Weather Station Reader
Demonstrates how to use the weather station client
"""

from weather_station_reader import WeatherStation3S
import time


def example_1_basic_read():
    """Example 1: Basic single read"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Single Read")
    print("="*80)
    
    # Create client with default parameters
    client = WeatherStation3S()
    
    # Connect to device
    print("\n1. Connecting to weather station...")
    if not client.connect():
        print("Failed to connect!")
        return
    
    try:
        # Read all sensors
        print("2. Reading sensor data...")
        readings = client.read_all_sensors()
        
        # Display results
        if readings:
            print("3. Displaying results...")
            client.display_readings(readings)
        else:
            print("No data received")
    
    finally:
        # Always disconnect
        client.disconnect()


def example_2_custom_parameters():
    """Example 2: Custom connection parameters"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Connection Parameters")
    print("="*80)
    
    # Create client with custom parameters
    client = WeatherStation3S(
        ip="192.168.1.5",      # Sungrow Logger IP
        port=505,              # Modbus TCP port
        slave_id=0xF7,         # Device slave ID
        timeout=10.0           # 10 second timeout
    )
    
    print(f"\nConnecting to {client.ip}:{client.port}")
    print(f"Slave ID: 0x{client.slave_id:02X} ({client.slave_id})")
    print(f"Timeout: {client.timeout} seconds")
    
    if client.connect():
        try:
            readings = client.read_all_sensors()
            client.display_readings(readings)
        finally:
            client.disconnect()


def example_3_raw_register_read():
    """Example 3: Read raw register values"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Read Raw Register Values")
    print("="*80)
    
    client = WeatherStation3S()
    
    if client.connect():
        try:
            # Read all 25 registers (8061-8085)
            print("\nReading registers 8061-8085 (25 registers)...")
            values = client.read_registers(8061, 25)
            
            if values:
                print(f"Successfully read {len(values)} registers\n")
                print(f"{'Register':<12} {'Value':<10} {'Hex':<10}")
                print("-" * 35)
                for i, val in enumerate(values):
                    addr = 8061 + i
                    print(f"{addr:<12} {val:<10} 0x{val:04X}")
            else:
                print("Failed to read registers")
        
        finally:
            client.disconnect()


def example_4_individual_sensors():
    """Example 4: Read individual sensors"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Read Individual Sensors")
    print("="*80)
    
    client = WeatherStation3S()
    
    if client.connect():
        try:
            # Read humidity (register 8061, 2 registers)
            print("\n1. Reading Humidity (Register 8061)...")
            humidity_vals = client.read_registers(8061, 2)
            if humidity_vals:
                humidity = humidity_vals[0] / 65536.0 * 100
                print(f"   Raw: {humidity_vals[0]}")
                print(f"   Humidity: {humidity:.1f}%")
            
            # Read temperature (register 8063, 2 registers)
            print("\n2. Reading Temperature (Register 8063)...")
            temp_vals = client.read_registers(8063, 2)
            if temp_vals:
                temp = (temp_vals[0] - 32768) / 32768.0 * 100
                print(f"   Raw: {temp_vals[0]}")
                print(f"   Temperature: {temp:.1f}°C")
            
            # Read wind speed (register 8082, 1 register)
            print("\n3. Reading Wind Speed (Register 8082)...")
            wind_vals = client.read_registers(8082, 1)
            if wind_vals:
                wind_speed = wind_vals[0] * 0.001
                print(f"   Raw: {wind_vals[0]}")
                print(f"   Wind Speed: {wind_speed:.2f} m/s")
            
            # Read solar irradiance (register 8085, 1 register)
            print("\n4. Reading Solar Irradiance (Register 8085)...")
            irr_vals = client.read_registers(8085, 1)
            if irr_vals:
                irradiance = irr_vals[0] * 0.1
                print(f"   Raw: {irr_vals[0]}")
                print(f"   Solar Irradiance: {irradiance:.1f} W/m²")
        
        finally:
            client.disconnect()


def example_5_continuous_monitoring():
    """Example 5: Continuous monitoring with intervals"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Continuous Monitoring (5 readings, 1 second apart)")
    print("="*80)
    
    client = WeatherStation3S()
    
    if client.connect():
        try:
            for i in range(1, 6):
                print(f"\n--- Reading #{i} ---")
                readings = client.read_all_sensors()
                
                if readings:
                    # Display compact format
                    print(f"Humidity:  {readings['humidity'].value:6.1f}%")
                    print(f"Temp:      {readings['temperature'].value:6.1f}°C")
                    print(f"Pressure:  {readings['pressure'].value:7.1f} hPa")
                    print(f"Wind:      {readings['wind_speed'].value:6.2f} m/s")
                    print(f"Solar:     {readings['solar_radiation'].value:7.1f} W/m²")
                
                if i < 5:
                    print("Waiting 1 second...")
                    time.sleep(1)
        
        finally:
            client.disconnect()


def example_6_error_handling():
    """Example 6: Error handling"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Error Handling and Timeouts")
    print("="*80)
    
    # Try with invalid IP (will timeout)
    print("\n1. Testing with invalid IP (will timeout)...")
    client = WeatherStation3S(
        ip="192.168.1.1",  # Non-existent gateway
        port=505,
        timeout=2.0  # Short timeout for demo
    )
    
    if client.connect():
        print("Connected (unexpected)")
    else:
        print("✓ Connection timeout handled gracefully")
    
    # Try with valid IP but invalid port
    print("\n2. Testing with invalid port...")
    client = WeatherStation3S(
        ip="192.168.1.5",
        port=9999,  # Wrong port
        timeout=2.0
    )
    
    if client.connect():
        print("Connected (unexpected)")
    else:
        print("✓ Connection refused handled gracefully")
    
    # Correct parameters
    print("\n3. Testing with correct parameters...")
    client = WeatherStation3S(
        ip="192.168.1.5",
        port=505,
        timeout=5.0
    )
    
    if client.connect():
        print("✓ Successfully connected")
        client.disconnect()
    else:
        print("⚠ Gateway may be offline")


def main():
    """Run all examples"""
    
    print("\n" + "="*80)
    print("3S-RH&AT&PS WEATHER STATION - USAGE EXAMPLES")
    print("="*80)
    
    examples = [
        ("Basic Single Read", example_1_basic_read),
        ("Custom Parameters", example_2_custom_parameters),
        ("Raw Register Read", example_3_raw_register_read),
        ("Individual Sensors", example_4_individual_sensors),
        ("Continuous Monitoring", example_5_continuous_monitoring),
        ("Error Handling", example_6_error_handling),
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect example (0-6): ").strip()
            
            if choice == "0":
                print("\nExiting...")
                break
            
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                name, func = examples[idx]
                print(f"\nRunning: {name}")
                func()
            else:
                print("Invalid selection")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted")
            break
        except ValueError:
            print("Please enter a number")


if __name__ == '__main__':
    main()
