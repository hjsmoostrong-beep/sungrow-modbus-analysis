#!/usr/bin/env python3
"""
Weather Station Web Server
Real-time weather data display with REST API.
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class WeatherWebHandler(BaseHTTPRequestHandler):
    """HTTP request handler for weather station."""
    
    # Class variables to share instances
    weather_station = None
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        # API endpoint: get current data
        if path == '/api/current':
            self.send_json(self.weather_station.get_current_data())
        
        # API endpoint: get history
        elif path == '/api/history':
            hours = int(query.get('hours', [24])[0])
            history = self.weather_station.get_history(hours)
            self.send_json(history)
        
        # API endpoint: get statistics
        elif path == '/api/stats':
            data = self.weather_station.get_current_data()
            self.send_json(data.get('statistics', {}))
        
        # API endpoint: get alerts
        elif path == '/api/alerts':
            data = self.weather_station.get_current_data()
            self.send_json(data.get('alerts', []))
        
        # API endpoint: get sensors
        elif path == '/api/sensors':
            self.send_json(self.weather_station.sensors)
        
        # Main dashboard page
        elif path == '/' or path == '/index.html':
            self.send_html(self.get_dashboard_html())
        
        # Historical data page
        elif path == '/history.html':
            self.send_html(self.get_history_html())
        
        # API documentation
        elif path == '/api.html':
            self.send_html(self.get_api_html())
        
        else:
            self.send_error(404, 'Not found')
    
    def send_json(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())
    
    def send_html(self, html):
        """Send HTML response."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        return
    
    def get_dashboard_html(self):
        """Generate main dashboard HTML."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Station Live Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status-bar {
            background: rgba(255,255,255,0.95);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .status-bar .time {
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .status-bar .status {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
        }
        
        .status-dot.offline {
            background: #f44336;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        }
        
        .card-title {
            color: #667eea;
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card-icon {
            font-size: 1.5em;
        }
        
        .reading {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .reading:last-child {
            border-bottom: none;
        }
        
        .reading-label {
            color: #666;
            font-size: 0.95em;
        }
        
        .reading-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
            font-family: 'Courier New', monospace;
        }
        
        .alert {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin-top: 10px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .alert.warning {
            background: #f8d7da;
            border-left-color: #f44336;
        }
        
        .alert.error {
            background: #f5222d;
            color: white;
            border-left-color: #d32f2f;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-label {
            font-size: 0.85em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 1.4em;
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }
        
        .loading {
            text-align: center;
            color: white;
            font-size: 1.1em;
            padding: 40px;
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .refresh-info {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        
        nav {
            background: rgba(255,255,255,0.95);
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        nav a {
            text-decoration: none;
            color: #667eea;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        
        nav a:hover {
            color: #764ba2;
        }
        
        nav a.active {
            border-bottom: 3px solid #667eea;
            padding-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌤️ Weather Station Live Dashboard</h1>
            <p>Real-time weather monitoring and data display</p>
        </header>
        
        <nav>
            <a href="/" class="active">Dashboard</a>
            <a href="/history.html">Historical Data</a>
            <a href="/api.html">API Documentation</a>
        </nav>
        
        <div class="status-bar">
            <div class="time" id="current-time">--:--:--</div>
            <div class="status">
                <div class="status-item">
                    <span class="status-dot" id="status-dot"></span>
                    <span id="status-text">Connecting...</span>
                </div>
                <div class="status-item">
                    Last update: <span id="last-update">--:--:--</span>
                </div>
            </div>
        </div>
        
        <div class="dashboard" id="dashboard">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading weather data...</p>
            </div>
        </div>
        
        <div class="refresh-info">
            <p>Updates every 10 seconds • Data auto-refreshes in background</p>
        </div>
    </div>
    
    <script>
        const API_URL = '/api';
        let lastUpdate = null;
        let refreshInterval = 10000; // 10 seconds
        
        // Update current time
        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = 
                now.toLocaleTimeString('en-US', { hour12: false });
        }
        
        // Format numbers
        function formatNumber(value, decimals = 1) {
            if (value === null || value === undefined) return 'N/A';
            return parseFloat(value).toFixed(decimals);
        }
        
        // Fetch and display weather data
        async function updateWeatherData() {
            try {
                const response = await fetch(API_URL + '/current');
                const data = await response.json();
                
                // Update status
                document.getElementById('status-dot').className = 'status-dot';
                document.getElementById('status-text').textContent = 'Online';
                
                // Update last update time
                const now = new Date();
                document.getElementById('last-update').textContent = 
                    now.toLocaleTimeString('en-US', { hour12: false });
                
                // Render dashboard
                renderDashboard(data);
                
                lastUpdate = now;
            } catch (error) {
                console.error('Error fetching data:', error);
                document.getElementById('status-dot').className = 'status-dot offline';
                document.getElementById('status-text').textContent = 'Offline';
            }
        }
        
        // Render dashboard cards
        function renderDashboard(data) {
            const dashboard = document.getElementById('dashboard');
            let html = '';
            
            if (!data.sensors || Object.keys(data.sensors).length === 0) {
                html = '<div class="card" style="grid-column: 1/-1;"><p>No sensor data available</p></div>';
                dashboard.innerHTML = html;
                return;
            }
            
            // Temperature Card
            if (data.sensors.bme280 || data.sensors.dht22) {
                const sensor = data.sensors.bme280 || data.sensors.dht22;
                const stats = data.statistics?.temperature || {};
                
                html += `
                    <div class="card">
                        <div class="card-title">
                            <span class="card-icon">🌡️</span>
                            Temperature
                        </div>
                        <div class="reading">
                            <span class="reading-label">Current</span>
                            <span class="reading-value">${formatNumber(sensor.temperature)}°C</span>
                        </div>
                        ${stats.min ? `
                        <div class="stats-grid">
                            <div class="stat-box">
                                <div class="stat-label">Min</div>
                                <div class="stat-value">${formatNumber(stats.min)}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-label">Max</div>
                                <div class="stat-value">${formatNumber(stats.max)}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-label">Avg</div>
                                <div class="stat-value">${formatNumber(stats.avg)}</div>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                `;
            }
            
            // Humidity Card
            if (data.sensors.bme280 || data.sensors.dht22) {
                const sensor = data.sensors.bme280 || data.sensors.dht22;
                const stats = data.statistics?.humidity || {};
                
                html += `
                    <div class="card">
                        <div class="card-title">
                            <span class="card-icon">💧</span>
                            Humidity
                        </div>
                        <div class="reading">
                            <span class="reading-label">Current</span>
                            <span class="reading-value">${formatNumber(sensor.humidity)}%</span>
                        </div>
                        ${stats.min ? `
                        <div class="stats-grid">
                            <div class="stat-box">
                                <div class="stat-label">Min</div>
                                <div class="stat-value">${formatNumber(stats.min)}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-label">Max</div>
                                <div class="stat-value">${formatNumber(stats.max)}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-label">Avg</div>
                                <div class="stat-value">${formatNumber(stats.avg)}</div>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                `;
            }
            
            // Pressure Card
            if (data.sensors.bme280) {
                html += `
                    <div class="card">
                        <div class="card-title">
                            <span class="card-icon">🔽</span>
                            Pressure
                        </div>
                        <div class="reading">
                            <span class="reading-label">Current</span>
                            <span class="reading-value">${formatNumber(data.sensors.bme280.pressure)}hPa</span>
                        </div>
                    </div>
                `;
            }
            
            // Wind Card
            if (data.sensors.wind) {
                const stats = data.statistics?.wind_speed || {};
                html += `
                    <div class="card">
                        <div class="card-title">
                            <span class="card-icon">💨</span>
                            Wind Speed
                        </div>
                        <div class="reading">
                            <span class="reading-label">Current</span>
                            <span class="reading-value">${formatNumber(data.sensors.wind.wind_speed, 2)}m/s</span>
                        </div>
                        <div class="reading">
                            <span class="reading-label">Gust</span>
                            <span class="reading-value">${formatNumber(data.sensors.wind.wind_gust, 2)}m/s</span>
                        </div>
                        ${stats.max ? `
                        <div class="stats-grid">
                            <div class="stat-box">
                                <div class="stat-label">Avg</div>
                                <div class="stat-value">${formatNumber(stats.avg, 2)}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-label">Max</div>
                                <div class="stat-value">${formatNumber(stats.max, 2)}</div>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                `;
            }
            
            // Rain Card
            if (data.sensors.rain) {
                html += `
                    <div class="card">
                        <div class="card-title">
                            <span class="card-icon">🌧️</span>
                            Rain
                        </div>
                        <div class="reading">
                            <span class="reading-label">Rain Rate</span>
                            <span class="reading-value">${formatNumber(data.sensors.rain.rain_rate, 1)}mm/h</span>
                        </div>
                    </div>
                `;
            }
            
            // UV Index Card
            if (data.sensors.uv) {
                const uvIndex = data.sensors.uv.uv_index;
                let uvLevel = 'Safe';
                if (uvIndex > 2) uvLevel = 'Low';
                if (uvIndex > 5) uvLevel = 'Moderate';
                if (uvIndex > 7) uvLevel = 'High';
                if (uvIndex > 10) uvLevel = 'Very High';
                
                html += `
                    <div class="card">
                        <div class="card-title">
                            <span class="card-icon">☀️</span>
                            UV Index
                        </div>
                        <div class="reading">
                            <span class="reading-label">Index</span>
                            <span class="reading-value">${formatNumber(uvIndex, 1)}</span>
                        </div>
                        <div class="reading">
                            <span class="reading-label">Level</span>
                            <span class="reading-value">${uvLevel}</span>
                        </div>
                    </div>
                `;
            }
            
            // Light Card
            if (data.sensors.light) {
                html += `
                    <div class="card">
                        <div class="card-title">
                            <span class="card-icon">💡</span>
                            Light Level
                        </div>
                        <div class="reading">
                            <span class="reading-label">Luminance</span>
                            <span class="reading-value">${formatNumber(data.sensors.light.light_level, 0)}lux</span>
                        </div>
                    </div>
                `;
            }
            
            // Alerts Card
            if (data.alerts && data.alerts.length > 0) {
                html += `
                    <div class="card" style="grid-column: 1/-1;">
                        <div class="card-title">
                            <span class="card-icon">⚠️</span>
                            Alerts & Warnings
                        </div>
                        ${data.alerts.map(alert => `
                            <div class="alert ${alert.severity}">
                                ${alert.message}
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            dashboard.innerHTML = html;
        }
        
        // Initialize
        updateTime();
        setInterval(updateTime, 1000);
        
        // Initial load
        updateWeatherData();
        
        // Auto-refresh
        setInterval(updateWeatherData, refreshInterval);
    </script>
</body>
</html>'''
    
    def get_history_html(self):
        """Generate historical data page."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Historical Weather Data</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        nav {
            background: rgba(255,255,255,0.95);
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        nav a {
            text-decoration: none;
            color: #667eea;
            font-weight: 500;
        }
        
        nav a.active {
            border-bottom: 3px solid #667eea;
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .chart-title {
            color: #667eea;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        canvas {
            max-height: 400px;
        }
        
        .controls {
            background: rgba(255,255,255,0.95);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        select, button {
            padding: 8px 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1em;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
        }
        
        button:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Historical Weather Data</h1>
        </header>
        
        <nav>
            <a href="/">Dashboard</a>
            <a href="/history.html" class="active">Historical Data</a>
            <a href="/api.html">API Documentation</a>
        </nav>
        
        <div class="controls">
            <label>Time range: 
                <select id="time-range">
                    <option value="6">Last 6 hours</option>
                    <option value="12">Last 12 hours</option>
                    <option value="24" selected>Last 24 hours</option>
                </select>
            </label>
            <button onclick="refreshCharts()">Refresh Charts</button>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Temperature Trend</div>
            <canvas id="tempChart"></canvas>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Humidity Trend</div>
            <canvas id="humidityChart"></canvas>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Pressure Trend</div>
            <canvas id="pressureChart"></canvas>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">Wind Speed Trend</div>
            <canvas id="windChart"></canvas>
        </div>
    </div>
    
    <script>
        let charts = {};
        
        async function loadHistoryData() {
            const hours = document.getElementById('time-range').value;
            const response = await fetch('/api/history?hours=' + hours);
            return await response.json();
        }
        
        async function refreshCharts() {
            const data = await loadHistoryData();
            
            const temperatures = [];
            const humidities = [];
            const pressures = [];
            const winds = [];
            const labels = [];
            
            data.forEach(point => {
                const date = new Date(point.timestamp);
                labels.push(date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
                
                if (point.sensors.bme280) {
                    temperatures.push(point.sensors.bme280.temperature);
                    humidities.push(point.sensors.bme280.humidity);
                    pressures.push(point.sensors.bme280.pressure);
                } else if (point.sensors.dht22) {
                    temperatures.push(point.sensors.dht22.temperature);
                    humidities.push(point.sensors.dht22.humidity);
                }
                
                if (point.sensors.wind) {
                    winds.push(point.sensors.wind.wind_speed);
                }
            });
            
            // Temperature Chart
            if (charts.temp) charts.temp.destroy();
            charts.temp = new Chart(document.getElementById('tempChart'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Temperature (°C)',
                        data: temperatures,
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244,67,54,0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
            
            // Humidity Chart
            if (charts.humidity) charts.humidity.destroy();
            charts.humidity = new Chart(document.getElementById('humidityChart'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Humidity (%)',
                        data: humidities,
                        borderColor: '#2196f3',
                        backgroundColor: 'rgba(33,150,243,0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
            
            // Pressure Chart
            if (charts.pressure) charts.pressure.destroy();
            charts.pressure = new Chart(document.getElementById('pressureChart'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Pressure (hPa)',
                        data: pressures,
                        borderColor: '#ff9800',
                        backgroundColor: 'rgba(255,152,0,0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
            
            // Wind Chart
            if (charts.wind) charts.wind.destroy();
            charts.wind = new Chart(document.getElementById('windChart'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Wind Speed (m/s)',
                        data: winds,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76,175,80,0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
        
        // Initial load
        document.getElementById('time-range').addEventListener('change', refreshCharts);
        refreshCharts();
    </script>
</body>
</html>'''
    
    def get_api_html(self):
        """Generate API documentation."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Station API Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        nav {
            background: rgba(255,255,255,0.95);
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        nav a {
            text-decoration: none;
            color: #667eea;
            font-weight: 500;
        }
        
        nav a.active {
            border-bottom: 3px solid #667eea;
        }
        
        .content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .api-endpoint {
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        
        .api-endpoint:last-child {
            border-bottom: none;
        }
        
        .endpoint-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .method {
            display: inline-block;
            padding: 4px 8px;
            background: #667eea;
            color: white;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 10px;
        }
        
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        
        pre {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            margin-top: 10px;
        }
        
        .description {
            margin-top: 10px;
            color: #666;
        }
        
        h2 {
            color: #667eea;
            margin-top: 30px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌤️ Weather Station API</h1>
            <p>Complete API Documentation</p>
        </header>
        
        <nav>
            <a href="/">Dashboard</a>
            <a href="/history.html">Historical Data</a>
            <a href="/api.html" class="active">API Documentation</a>
        </nav>
        
        <div class="content">
            <h2>Available Endpoints</h2>
            
            <div class="api-endpoint">
                <div class="endpoint-title">
                    <span class="method">GET</span>
                    <code>/api/current</code>
                </div>
                <div class="description">
                    Get current weather data including all sensor readings, statistics, and alerts.
                </div>
                <pre>{
  "timestamp": "2025-12-10T14:30:45.123456",
  "datetime": "2025-12-10 14:30:45",
  "sensors": {
    "bme280": {
      "temperature": 22.5,
      "humidity": 55.2,
      "pressure": 1013.4
    },
    "wind": {
      "wind_speed": 3.2,
      "wind_gust": 5.1
    }
  },
  "statistics": {
    "temperature": {
      "current": 22.5,
      "min": 18.2,
      "max": 26.1,
      "avg": 22.1
    }
  },
  "alerts": []
}</pre>
            </div>
            
            <div class="api-endpoint">
                <div class="endpoint-title">
                    <span class="method">GET</span>
                    <code>/api/history</code>
                </div>
                <div class="description">
                    Get historical weather data. Parameters: <code>hours</code> (1-24, default 24)
                </div>
                <p>Example: <code>/api/history?hours=12</code></p>
            </div>
            
            <div class="api-endpoint">
                <div class="endpoint-title">
                    <span class="method">GET</span>
                    <code>/api/stats</code>
                </div>
                <div class="description">
                    Get calculated statistics (min, max, average) for all readings.
                </div>
            </div>
            
            <div class="api-endpoint">
                <div class="endpoint-title">
                    <span class="method">GET</span>
                    <code>/api/alerts</code>
                </div>
                <div class="description">
                    Get current alerts and warnings based on configured thresholds.
                </div>
            </div>
            
            <div class="api-endpoint">
                <div class="endpoint-title">
                    <span class="method">GET</span>
                    <code>/api/sensors</code>
                </div>
                <div class="description">
                    Get list of configured sensors and their status.
                </div>
            </div>
            
            <h2>Sensor Types Supported</h2>
            
            <ul style="margin: 15px 0;">
                <li><strong>BME280:</strong> Temperature, Humidity, Pressure (I2C)</li>
                <li><strong>DHT22:</strong> Temperature, Humidity (GPIO)</li>
                <li><strong>Anemometer:</strong> Wind Speed, Wind Gust (GPIO)</li>
                <li><strong>Rain Gauge:</strong> Rain Rate (GPIO)</li>
                <li><strong>UV Sensor:</strong> UV Index (I2C)</li>
                <li><strong>Light Sensor:</strong> Ambient Light Level (I2C)</li>
            </ul>
            
            <h2>Alert Thresholds</h2>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="background: #f5f5f5;">
                    <th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Alert Type</th>
                    <th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Threshold</th>
                    <th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Severity</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 10px;">Temperature High</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">≥ 40°C</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">Warning</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 10px;">Temperature Low</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">≤ -10°C</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">Warning</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 10px;">Humidity High</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">≥ 95%</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">Info</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 10px;">Wind Speed High</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">≥ 50m/s</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">Warning</td>
                </tr>
            </table>
            
            <h2>CORS Enabled</h2>
            <p style="margin-top: 15px;">All API endpoints support CORS and can be accessed from any origin.</p>
        </div>
    </div>
</body>
</html>'''

class WeatherWebServer:
    """Weather station web server."""
    
    def __init__(self, weather_station, host='0.0.0.0', port=8080):
        """
        Initialize web server.
        
        Args:
            weather_station: WeatherStation instance
            host: Host to bind to
            port: Port to listen on
        """
        self.weather_station = weather_station
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the web server."""
        # Set class variable for request handler
        WeatherWebHandler.weather_station = self.weather_station
        
        self.server = HTTPServer((self.host, self.port), WeatherWebHandler)
        
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        
        print(f"Weather station web server started: http://{self.host}:{self.port}")
    
    def _run_server(self):
        """Run server in thread."""
        self.server.serve_forever()
    
    def stop(self):
        """Stop the web server."""
        if self.server:
            self.server.shutdown()

# Example usage
if __name__ == '__main__':
    from weather_station import WeatherStation
    
    # Create weather station
    station = WeatherStation()
    
    # Add sensors
    station.add_sensor('bme280', 'BME280', 'outdoor')
    station.add_sensor('dht22', 'DHT22', 'indoor')
    station.add_sensor('wind', 'Anemometer', 'outdoor')
    station.add_sensor('rain', 'Rain Gauge', 'outdoor')
    station.add_sensor('uv', 'UV Sensor', 'outdoor')
    station.add_sensor('light', 'Light Sensor', 'outdoor')
    
    # Start monitoring
    print("Starting weather station...")
    station.start_monitoring(interval=10)  # Collect every 10 seconds
    
    # Start web server
    web_server = WeatherWebServer(station, port=8080)
    web_server.start()
    
    try:
        print("\nWeather Station Dashboard: http://localhost:8080")
        print("Press Ctrl+C to stop...")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping weather station...")
        station.stop_monitoring()
        web_server.stop()
        print("Done!")
