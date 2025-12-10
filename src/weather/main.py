#!/usr/bin/env python3
"""
Weather Station Quick Start
Run this to start the weather station web server.
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Start weather station."""
    print("\n" + "="*60)
    print("🌤️  WEATHER STATION SYSTEM")
    print("="*60 + "\n")
    
    try:
        from weather_station import WeatherStation
        from weather_web_server import WeatherWebServer
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("\nMake sure weather_station.py and weather_web_server.py are in the same directory.")
        return 1
    
    # Create weather station
    print("📡 Initializing weather station...")
    station = WeatherStation(max_history=1440)  # 24 hours at 1-min intervals
    
    # Add sensors
    print("🔧 Configuring sensors...")
    sensors = [
        ('bme280', 'BME280', 'outdoor (primary)'),
        ('dht22', 'DHT22', 'indoor (backup)'),
        ('wind', 'Anemometer', 'outdoor'),
        ('rain', 'Rain Gauge', 'outdoor'),
        ('uv', 'UV Sensor', 'outdoor'),
        ('light', 'Light Sensor', 'outdoor'),
        ('sungrow', 'Sungrow Inverter', 'Modbus 192.168.1.5')
    ]
    
    for sensor_id, sensor_type, location in sensors:
        station.add_sensor(sensor_id, sensor_type, location)
        print(f"  ✓ {sensor_type:20} ({location})")
    
    # Set alert thresholds
    print("\n⚠️  Alert thresholds:")
    print(f"  Temperature: {station.alert_thresholds['temp_low']}°C - {station.alert_thresholds['temp_high']}°C")
    print(f"  Humidity: {station.alert_thresholds['humidity_low']}% - {station.alert_thresholds['humidity_high']}%")
    print(f"  Wind: {station.alert_thresholds['wind_speed_high']}m/s (max)")
    
    # Start monitoring
    print("\n📊 Starting data collection...")
    print("  Interval: 10 seconds (for demo)")
    station.start_monitoring(interval=10)
    time.sleep(2)  # Let it start
    
    # Start web server
    print("\n🌐 Starting web server...")
    try:
        web_server = WeatherWebServer(station, host='0.0.0.0', port=8080)
        web_server.start()
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        station.stop_monitoring()
        return 1
    
    # Display access information
    print("\n" + "="*60)
    print("✅ WEATHER STATION READY")
    print("="*60)
    print("\n📱 Access dashboard at:")
    print("   http://localhost:8080")
    print("   http://127.0.0.1:8080")
    print(f"   http://<your-ip>:8080")
    
    print("\n📖 Available pages:")
    print("   / or /index.html        - Live Dashboard")
    print("   /history.html           - Historical Data & Charts")
    print("   /api.html               - API Documentation")
    
    print("\n🔌 API Endpoints:")
    print("   GET /api/current        - Current reading")
    print("   GET /api/history        - Historical data")
    print("   GET /api/stats          - Statistics")
    print("   GET /api/alerts         - Current alerts")
    print("   GET /api/sensors        - Sensor status")
    
    print("\n💾 Data Storage:")
    print("   Last reading:  Saved in memory (max 1440 points)")
    print("   Data export:   /api/current or /api/history")
    print("   File save:     station.save_to_file('filename.json')")
    
    print("\n⌨️  Controls:")
    print("   Ctrl+C  - Stop weather station")
    
    print("\n" + "="*60 + "\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...\n")
        
        # Save data before exiting
        print("💾 Saving collected data...")
        try:
            station.save_to_file('weather_data.json')
            print("   ✓ Data saved to: weather_data.json")
        except Exception as e:
            print(f"   ⚠️  Could not save: {e}")
        
        # Stop services
        station.stop_monitoring()
        web_server.stop()
        
        print("✓ Weather station stopped\n")
        return 0

if __name__ == '__main__':
    sys.exit(main())
