#!/usr/bin/env python3
"""
Quick start script for weather station web monitor
"""

from weather_station_web import WeatherStationWebMonitor


def main():
    """Start the web monitor"""
    
    # Create monitor with default settings
    monitor = WeatherStationWebMonitor(
        gateway_ip="192.168.1.5",      # Sungrow Logger IP
        gateway_port=505,               # Modbus port
        web_port=8080,                  # Web server port
        update_interval=2               # Update every 2 seconds
    )
    
    # Start the server
    monitor.start()


if __name__ == '__main__':
    main()
