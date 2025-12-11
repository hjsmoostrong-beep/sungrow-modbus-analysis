#!/usr/bin/env python3
"""
3S-RH&AT&PS Weather Station Web Monitor
Real-time monitoring with web dashboard
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path
from weather_station_reader import WeatherStation3S


class WeatherStationWebServer(BaseHTTPRequestHandler):
    """HTTP request handler for weather station web interface"""
    
    # Class variable to share weather data across requests
    current_data = {
        'humidity': {'value': 0, 'unit': '%'},
        'temperature': {'value': 0, 'unit': '°C'},
        'pressure': {'value': 0, 'unit': 'hPa'},
        'wind_speed': {'value': 0, 'unit': 'm/s'},
        'solar_radiation': {'value': 0, 'unit': 'W/m²'},
        'timestamp': 'N/A',
        'status': 'Waiting...'
    }
    
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/data':
            self.serve_json_data()
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """Serve HTML dashboard"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3S-RH&AT&PS Weather Station Monitor</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .status {{
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 1.1em;
        }}
        
        .status.ok {{ color: #4ade80; }}
        .status.connecting {{ color: #fbbf24; }}
        .status.error {{ color: #ef4444; }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}
        
        .card-icon {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
        
        .card-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .card-value {{
            font-size: 2.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .card-unit {{
            color: #999;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            text-align: center;
            color: white;
            font-size: 0.95em;
            margin-bottom: 15px;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            opacity: 0.8;
            margin-top: 30px;
            font-size: 0.9em;
        }}
        
        .gauge {{
            width: 100%;
            height: 200px;
            margin-top: 15px;
        }}
        
        .spinner {{
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .alert {{
            background: #fef08a;
            border-left: 4px solid #fbbf24;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌤️ Weather Station Monitor</h1>
            <p>3S-RH&AT&PS Real-Time Data Display</p>
        </header>
        
        <div class="status connecting">
            <span class="spinner"></span>Loading data...
        </div>
        
        <div class="timestamp" id="timestamp">
            Last Updated: Connecting...
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-icon">💧</div>
                <div class="card-label">Humidity</div>
                <div class="card-value" id="humidity">--</div>
                <div class="card-unit">%</div>
            </div>
            
            <div class="card">
                <div class="card-icon">🌡️</div>
                <div class="card-label">Temperature</div>
                <div class="card-value" id="temperature">--</div>
                <div class="card-unit">°C</div>
            </div>
            
            <div class="card">
                <div class="card-icon">⛅</div>
                <div class="card-label">Pressure</div>
                <div class="card-value" id="pressure">--</div>
                <div class="card-unit">hPa</div>
            </div>
            
            <div class="card">
                <div class="card-icon">💨</div>
                <div class="card-label">Wind Speed</div>
                <div class="card-value" id="wind_speed">--</div>
                <div class="card-unit">m/s</div>
            </div>
            
            <div class="card">
                <div class="card-icon">☀️</div>
                <div class="card-label">Solar Irradiance</div>
                <div class="card-value" id="solar_radiation">--</div>
                <div class="card-unit">W/m²</div>
            </div>
            
            <div class="card">
                <div class="card-icon">📡</div>
                <div class="card-label">Gateway Status</div>
                <div class="card-value" id="status">--</div>
                <div class="card-unit">Connected</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Gateway: 192.168.1.5:505 | Device: 3S-RH&AT&PS | Updates every 2 seconds</p>
        </div>
    </div>
    
    <script>
        // Update data every 2 seconds
        setInterval(function() {{
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('humidity').textContent = data.humidity.value.toFixed(1);
                    document.getElementById('temperature').textContent = data.temperature.value.toFixed(1);
                    document.getElementById('pressure').textContent = data.pressure.value.toFixed(1);
                    document.getElementById('wind_speed').textContent = data.wind_speed.value.toFixed(2);
                    document.getElementById('solar_radiation').textContent = data.solar_radiation.value.toFixed(0);
                    document.getElementById('status').textContent = data.status === 'OK' ? '[OK]' : data.status;
                    document.getElementById('timestamp').textContent = 'Last Updated: ' + data.timestamp;
                    
                    // Update status indicator
                    const statusDiv = document.querySelector('.status');
                    statusDiv.classList.remove('connecting', 'ok', 'error');
                    statusDiv.classList.add(data.status === 'OK' ? 'ok' : 'error');
                    statusDiv.innerHTML = data.status === 'OK' ? '[OK] Connected' : '[ERROR] Connection Error';
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    document.querySelector('.status').classList.remove('connecting', 'ok');
                    document.querySelector('.status').classList.add('error');
                    document.querySelector('.status').textContent = '[ERROR] Connection Error';
                }});
        }}, 2000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_json_data(self):
        """Serve current data as JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(self.current_data, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class WeatherStationWebMonitor:
    """Manager for weather station web server"""
    
    def __init__(self, gateway_ip="192.168.1.5", gateway_port=505, 
                 web_port=8080, update_interval=2):
        """
        Initialize web monitor
        
        Args:
            gateway_ip: Modbus gateway IP
            gateway_port: Modbus gateway port
            web_port: Web server port
            update_interval: Seconds between updates
        """
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        self.web_port = web_port
        self.update_interval = update_interval
        
        self.client = WeatherStation3S(
            ip=gateway_ip,
            port=gateway_port,
            timeout=5.0
        )
        
        self.server = None
        self.update_thread = None
        self.running = False
    
    def update_weather_data(self):
        """Background thread to update weather data"""
        
        print(f"Connecting to weather station at {self.gateway_ip}:{self.gateway_port}...")
        
        if not self.client.connect():
            print("Failed to connect to weather station")
            WeatherStationWebServer.current_data['status'] = 'Connection Error'
            return
        
        print("[OK] Connected to weather station")
        
        try:
            while self.running:
                try:
                    readings = self.client.read_all_sensors()
                    
                    if readings:
                        # Update shared data
                        WeatherStationWebServer.current_data = {
                            'humidity': {
                                'value': readings['humidity'].value,
                                'unit': readings['humidity'].unit
                            },
                            'temperature': {
                                'value': readings['temperature'].value,
                                'unit': readings['temperature'].unit
                            },
                            'pressure': {
                                'value': readings['pressure'].value,
                                'unit': readings['pressure'].unit
                            },
                            'wind_speed': {
                                'value': readings['wind_speed'].value,
                                'unit': readings['wind_speed'].unit
                            },
                            'solar_radiation': {
                                'value': readings['solar_radiation'].value,
                                'unit': readings['solar_radiation'].unit
                            },
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'status': 'OK'
                        }
                    else:
                        WeatherStationWebServer.current_data['status'] = 'Read Error'
                
                except Exception as e:
                    print(f"Error reading data: {e}")
                    WeatherStationWebServer.current_data['status'] = 'Error'
                
                time.sleep(self.update_interval)
        
        finally:
            self.client.disconnect()
    
    def start(self):
        """Start web server"""
        
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_weather_data, daemon=True)
        self.update_thread.start()
        
        # Start HTTP server
        self.server = HTTPServer(('0.0.0.0', self.web_port), WeatherStationWebServer)
        
        print(f"\n{'='*70}")
        print("3S-RH&AT&PS WEATHER STATION WEB MONITOR")
        print(f"{'='*70}")
        print(f"[OK] Web Server started at http://localhost:{self.web_port}")
        print(f"[OK] Updating data every {self.update_interval} seconds")
        print(f"[OK] Gateway: {self.gateway_ip}:{self.gateway_port}")
        print(f"\nPress Ctrl+C to stop")
        print(f"{'='*70}\n")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n[OK] Shutting down...")
            self.stop()
    
    def stop(self):
        """Stop web server"""
        self.running = False
        if self.server:
            self.server.shutdown()
        print("[OK] Server stopped")


def main():
    """Main execution"""
    
    monitor = WeatherStationWebMonitor(
        gateway_ip="192.168.1.5",
        gateway_port=505,
        web_port=8080,
        update_interval=2
    )
    
    monitor.start()


if __name__ == '__main__':
    main()
