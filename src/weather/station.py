#!/usr/bin/env python3
"""
Weather Station Data Logger
Real-time temperature, humidity, pressure, and wind data collection and display.
Supports multiple sensor types and protocols.
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from collections import deque
import statistics

class WeatherStation:
    """Collect and manage weather data from multiple sensors."""
    
    def __init__(self, max_history=1440):  # 24 hours at 1-min intervals
        """
        Initialize weather station.
        
        Args:
            max_history: Maximum number of data points to keep in memory
        """
        self.max_history = max_history
        self.data_history = deque(maxlen=max_history)
        self.current_data = {}
        self.lock = threading.Lock()
        self.running = False
        self.sensors = {}
        self.alert_thresholds = {
            'temp_high': 40,      # °C
            'temp_low': -10,      # °C
            'humidity_high': 95,  # %
            'humidity_low': 10,   # %
            'pressure_high': 1050, # hPa
            'pressure_low': 950,  # hPa
            'wind_speed_high': 50, # m/s
        }
        
    def add_sensor(self, sensor_id, sensor_type, location=''):
        """Register a new sensor."""
        self.sensors[sensor_id] = {
            'type': sensor_type,
            'location': location,
            'last_reading': None,
            'status': 'offline'
        }
        
    def read_bme280(self, i2c_address=0x77):
        """
        Simulate BME280 temperature, humidity, pressure sensor reading.
        Real implementation would use Adafruit_BME280 library.
        """
        import random
        
        # Simulate realistic sensor data with daily variation
        hour = datetime.now().hour
        base_temp = 15 + 10 * (hour / 24)  # Vary 15-25°C through day
        
        return {
            'temperature': base_temp + random.uniform(-2, 2),
            'humidity': 45 + random.uniform(-5, 5),
            'pressure': 1013 + random.uniform(-3, 3)
        }
    
    def read_dht22(self, gpio_pin=4):
        """
        Simulate DHT22 temperature and humidity sensor.
        Real implementation would use Adafruit_DHT library.
        """
        import random
        
        hour = datetime.now().hour
        base_temp = 18 + 8 * (hour / 24)
        
        return {
            'temperature': base_temp + random.uniform(-1.5, 1.5),
            'humidity': 50 + random.uniform(-8, 8)
        }
    
    def read_wind_sensor(self, gpio_pin=17):
        """
        Simulate anemometer wind speed reading.
        Real: Count GPIO pulses; 1 pulse = 2.4km/h = 0.67m/s
        """
        import random
        import math
        
        hour = datetime.now().hour
        # Wind typically increases in afternoon
        base_wind = 2 + 3 * math.sin(hour * 3.14 / 24)
        
        return {
            'wind_speed': max(0, base_wind + random.uniform(-1, 1)),
            'wind_gust': max(0, base_wind + 2 + random.uniform(-1, 1))
        }
    
    def read_rain_gauge(self, gpio_pin=27):
        """
        Simulate rain gauge (tipping bucket).
        Real: Each tip = 0.2794mm of rain
        """
        import random
        
        # Randomly simulate rain events (20% chance)
        if random.random() < 0.05:  # 5% chance of tipping event
            return {'rain_rate': random.uniform(2, 10)}  # mm/hour
        return {'rain_rate': 0}
    
    def read_uv_sensor(self, i2c_address=0x38):
        """
        Simulate UV index sensor (ML8511 or similar).
        Real: Analog reading converted to UV index.
        """
        import random
        import math
        
        hour = datetime.now().hour
        # UV highest at midday
        base_uv = 8 * abs(math.sin(hour * 3.14 / 24))
        
        return {
            'uv_index': base_uv + random.uniform(-0.5, 0.5)
        }
    
    def read_light_sensor(self, i2c_address=0x23):
        """
        Simulate ambient light sensor (BH1750).
        Real: Returns lux value via I2C.
        """
        import random
        import math
        
        hour = datetime.now().hour
        # Light peaks at midday
        base_light = 10000 * abs(math.sin(hour * 3.14 / 24))
        
        return {
            'light_level': base_light + random.uniform(-1000, 1000)
        }
    
    def collect_data(self):
        """Collect data from all configured sensors."""
        timestamp = datetime.now()
        
        data_point = {
            'timestamp': timestamp.isoformat(),
            'datetime': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sensors': {}
        }
        
        # Read from each configured sensor
        readings = {}
        
        # BME280 (combined sensor)
        if 'bme280' in self.sensors:
            try:
                readings['bme280'] = self.read_bme280()
                self.sensors['bme280']['status'] = 'online'
            except Exception as e:
                self.sensors['bme280']['status'] = f'error: {e}'
        
        # DHT22 (temperature/humidity)
        if 'dht22' in self.sensors:
            try:
                readings['dht22'] = self.read_dht22()
                self.sensors['dht22']['status'] = 'online'
            except Exception as e:
                self.sensors['dht22']['status'] = f'error: {e}'
        
        # Wind sensor
        if 'wind' in self.sensors:
            try:
                readings['wind'] = self.read_wind_sensor()
                self.sensors['wind']['status'] = 'online'
            except Exception as e:
                self.sensors['wind']['status'] = f'error: {e}'
        
        # Rain gauge
        if 'rain' in self.sensors:
            try:
                readings['rain'] = self.read_rain_gauge()
                self.sensors['rain']['status'] = 'online'
            except Exception as e:
                self.sensors['rain']['status'] = f'error: {e}'
        
        # UV sensor
        if 'uv' in self.sensors:
            try:
                readings['uv'] = self.read_uv_sensor()
                self.sensors['uv']['status'] = 'online'
            except Exception as e:
                self.sensors['uv']['status'] = f'error: {e}'
        
        # Light sensor
        if 'light' in self.sensors:
            try:
                readings['light'] = self.read_light_sensor()
                self.sensors['light']['status'] = 'online'
            except Exception as e:
                self.sensors['light']['status'] = f'error: {e}'
        
        # Sungrow inverter (Modbus unit 1)
        if 'sungrow' in self.sensors:
            try:
                readings['sungrow'] = self.read_sungrow_inverter()
                self.sensors['sungrow']['status'] = 'online'
            except Exception as e:
                self.sensors['sungrow']['status'] = f'error: {e}'
        
        data_point['sensors'] = readings
        
        # Store and update
        with self.lock:
            self.data_history.append(data_point)
            self.current_data = data_point
            self.current_data['statistics'] = self.calculate_statistics()
            self.current_data['alerts'] = self.check_alerts()
        
        return data_point
    
    def calculate_statistics(self):
        """Calculate statistics from historical data."""
        if not self.data_history or len(self.data_history) < 2:
            return {}
        
        stats = {}
        
        # Temperature stats (if available)
        temps = []
        humidities = []
        wind_speeds = []
        
        for point in self.data_history:
            if 'bme280' in point['sensors']:
                temps.append(point['sensors']['bme280'].get('temperature', 0))
                humidities.append(point['sensors']['bme280'].get('humidity', 0))
            elif 'dht22' in point['sensors']:
                temps.append(point['sensors']['dht22'].get('temperature', 0))
                humidities.append(point['sensors']['dht22'].get('humidity', 0))
            
            if 'wind' in point['sensors']:
                wind_speeds.append(point['sensors']['wind'].get('wind_speed', 0))
        
        if temps:
            stats['temperature'] = {
                'current': round(temps[-1], 1),
                'min': round(min(temps), 1),
                'max': round(max(temps), 1),
                'avg': round(statistics.mean(temps), 1),
            }
        
        if humidities:
            stats['humidity'] = {
                'current': round(humidities[-1], 1),
                'min': round(min(humidities), 1),
                'max': round(max(humidities), 1),
                'avg': round(statistics.mean(humidities), 1),
            }
        
        if wind_speeds:
            stats['wind_speed'] = {
                'current': round(wind_speeds[-1], 2),
                'avg': round(statistics.mean(wind_speeds), 2),
                'max': round(max(wind_speeds), 2),
            }
        
        return stats
    
    def check_alerts(self):
        """Check for threshold violations."""
        alerts = []
        
        if not self.current_data or 'sensors' not in self.current_data:
            return alerts
        
        sensors = self.current_data['sensors']
        
        # Temperature checks
        if 'bme280' in sensors:
            temp = sensors['bme280'].get('temperature')
            if temp and temp > self.alert_thresholds['temp_high']:
                alerts.append({
                    'type': 'temp_high',
                    'message': f'High temperature: {temp:.1f}°C',
                    'severity': 'warning'
                })
            elif temp and temp < self.alert_thresholds['temp_low']:
                alerts.append({
                    'type': 'temp_low',
                    'message': f'Low temperature: {temp:.1f}°C',
                    'severity': 'warning'
                })
        
        # Humidity checks
        if 'bme280' in sensors:
            humidity = sensors['bme280'].get('humidity')
            if humidity and humidity > self.alert_thresholds['humidity_high']:
                alerts.append({
                    'type': 'humidity_high',
                    'message': f'High humidity: {humidity:.1f}%',
                    'severity': 'info'
                })
        
        # Wind speed checks
        if 'wind' in sensors:
            wind = sensors['wind'].get('wind_speed')
            if wind and wind > self.alert_thresholds['wind_speed_high']:
                alerts.append({
                    'type': 'wind_high',
                    'message': f'High wind: {wind:.1f} m/s',
                    'severity': 'warning'
                })
        
        return alerts
    
    def read_sungrow_inverter(self, unit_id=1):
        """Simulate reading Sungrow solar inverter data from Modbus registers."""
        import random
        import math
        
        # Simulate solar radiation (W/m²) - correlates with time of day
        hour = time.localtime().tm_hour
        base_radiation = max(0, 800 * math.sin((hour - 6) * math.pi / 12)) if 6 <= hour <= 18 else 0
        radiation = base_radiation + random.uniform(-50, 50)
        
        # Simulate inverter output (W) - correlates with solar radiation
        dc_power = radiation * 0.85 * random.uniform(0.9, 1.1)
        
        # DC side (PV array)
        dc_voltage = 300 + random.uniform(-10, 10)
        dc_current = dc_power / (dc_voltage + 0.1) if dc_voltage > 0 else 0
        
        # AC voltage (grid, typically 230V single phase or 380V 3-phase)
        ac_voltage_phase = [230 + random.uniform(-5, 5) for _ in range(3)]
        ac_power = dc_power * 0.95  # Account for inverter losses
        ac_current_phase = [ac_power / (voltage * 0.95 + 0.1) for voltage in ac_voltage_phase]
        
        # Energy counters
        today_energy = 15.5 + random.uniform(0, 2)  # kWh
        total_energy = 45280.3 + random.uniform(0, 0.5)  # kWh cumulative
        
        # Inverter status (0=standby, 1=normal, 2=fault)
        status = 1 if ac_power > 100 else 0
        
        # Temperature inside inverter
        inverter_temp = 35 + (ac_power / 5000) + random.uniform(-2, 2)
        
        return {
            'dc_voltage': round(dc_voltage, 2),
            'dc_current': round(dc_current, 2),
            'dc_power': round(dc_power, 2),
            'ac_voltage_phase1': round(ac_voltage_phase[0], 2),
            'ac_voltage_phase2': round(ac_voltage_phase[1], 2),
            'ac_voltage_phase3': round(ac_voltage_phase[2], 2),
            'ac_current_phase1': round(ac_current_phase[0], 2),
            'ac_current_phase2': round(ac_current_phase[1], 2),
            'ac_current_phase3': round(ac_current_phase[2], 2),
            'ac_power': round(ac_power, 2),
            'efficiency': round((ac_power / (dc_power + 1) * 100) if dc_power > 0 else 0, 2),
            'today_energy': round(today_energy, 2),
            'total_energy': round(total_energy, 2),
            'inverter_status': status,
            'inverter_temp': round(inverter_temp, 2),
            'solar_radiation': round(radiation, 2),
            'unit_id': unit_id
        }
    
    def start_monitoring(self, interval=60):
        """Start continuous monitoring thread."""
        self.running = True
        
        def monitor_loop():
            while self.running:
                try:
                    self.collect_data()
                    time.sleep(interval)
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False
    
    def get_current_data(self):
        """Get current data snapshot."""
        with self.lock:
            return json.loads(json.dumps(self.current_data, default=str))
    
    def get_history(self, hours=24):
        """Get historical data."""
        cutoff = time.time() - (hours * 3600)
        
        with self.lock:
            return list(self.data_history)
    
    def save_to_file(self, filename='weather_data.json'):
        """Save current data to JSON file."""
        data = {
            'current': self.get_current_data(),
            'history': self.get_history()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filename

# Example usage
if __name__ == '__main__':
    # Create station
    station = WeatherStation()
    
    # Add sensors
    station.add_sensor('bme280', 'BME280', 'outdoor')
    station.add_sensor('dht22', 'DHT22', 'indoor')
    station.add_sensor('wind', 'Anemometer', 'outdoor')
    station.add_sensor('rain', 'Rain Gauge', 'outdoor')
    station.add_sensor('uv', 'UV Sensor', 'outdoor')
    station.add_sensor('light', 'Light Sensor', 'outdoor')
    
    # Start monitoring
    print("Starting weather station monitoring...")
    station.start_monitoring(interval=10)  # Collect every 10 seconds for demo
    
    # Let it run for demo
    try:
        for i in range(6):
            time.sleep(10)
            current = station.get_current_data()
            print(f"\n[{current['datetime']}]")
            print(f"Sensors: {list(current['sensors'].keys())}")
            if 'statistics' in current:
                print(f"Stats: {json.dumps(current['statistics'], indent=2)}")
    except KeyboardInterrupt:
        print("\nStopping weather station...")
    finally:
        station.stop_monitoring()
        station.save_to_file()
        print("Data saved to weather_data.json")
