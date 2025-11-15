#!/usr/bin/env python3
"""
PROJECT SENTINEL - MONITORING DASHBOARD
Cameroon Defense Force OSINT Analysis System
Web-based monitoring dashboard with real-time metrics
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from pathlib import Path
import uvicorn
from system_monitor import SentinelSystemMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PROJECT SENTINEL - Monitoring Dashboard",
    description="Real-time system monitoring for Cameroon Defense Intelligence Platform",
    version="1.0.0"
)

# Initialize system monitor
monitor = SentinelSystemMonitor()

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, data: dict):
        """Broadcast data to all connected clients"""
        if not self.active_connections:
            return
        
        message = json.dumps(data, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main monitoring dashboard"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROJECT SENTINEL - System Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0, 255, 136, 0.1);
            border-bottom: 2px solid #00ff88;
            padding: 1rem 2rem;
            text-align: center;
        }
        
        .header h1 {
            color: #00ff88;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            color: #a0a0a0;
            font-size: 1rem;
        }
        
        .container {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        }
        
        .metric-card h3 {
            color: #00ff88;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-unit {
            color: #a0a0a0;
            font-size: 0.9rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-healthy {
            background-color: #00ff88;
            box-shadow: 0 0 10px #00ff88;
        }
        
        .status-unhealthy {
            background-color: #ff4444;
            box-shadow: 0 0 10px #ff4444;
        }
        
        .status-warning {
            background-color: #ffaa00;
            box-shadow: 0 0 10px #ffaa00;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .service-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 8px;
            padding: 1rem;
        }
        
        .service-header {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .service-name {
            font-weight: bold;
            color: #ffffff;
        }
        
        .service-response-time {
            color: #a0a0a0;
            font-size: 0.9rem;
        }
        
        .alerts-section {
            background: rgba(255, 68, 68, 0.1);
            border: 1px solid #ff4444;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .alerts-section h3 {
            color: #ff4444;
            margin-bottom: 1rem;
        }
        
        .alert-item {
            background: rgba(255, 68, 68, 0.2);
            border-left: 4px solid #ff4444;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
        }
        
        .alert-severity {
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.8rem;
        }
        
        .alert-critical { color: #ff4444; }
        .alert-high { color: #ff8844; }
        .alert-medium { color: #ffaa44; }
        .alert-low { color: #ffdd44; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        
        .progress-fill {
            height: 100%;
            transition: width 0.3s ease;
            border-radius: 4px;
        }
        
        .progress-normal { background: #00ff88; }
        .progress-warning { background: #ffaa00; }
        .progress-danger { background: #ff4444; }
        
        .timestamp {
            color: #a0a0a0;
            font-size: 0.8rem;
            text-align: center;
            margin-top: 2rem;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .connected {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border: 1px solid #00ff88;
        }
        
        .disconnected {
            background: rgba(255, 68, 68, 0.2);
            color: #ff4444;
            border: 1px solid #ff4444;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">Connecting...</div>
    
    <div class="header">
        <h1>PROJECT SENTINEL</h1>
        <p>System Performance Monitor - Cameroon Defense Intelligence Platform</p>
    </div>
    
    <div class="container">
        <!-- System Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>CPU Usage</h3>
                <div class="metric-value" id="cpuUsage">--</div>
                <div class="metric-unit">percentage</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpuProgress"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>Memory Usage</h3>
                <div class="metric-value" id="memoryUsage">--</div>
                <div class="metric-unit">percentage</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memoryProgress"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>Disk Usage</h3>
                <div class="metric-value" id="diskUsage">--</div>
                <div class="metric-unit">percentage</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="diskProgress"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>Active Services</h3>
                <div class="metric-value" id="activeServices">-- / --</div>
                <div class="metric-unit">healthy services</div>
            </div>
        </div>
        
        <!-- Services Status -->
        <div class="services-grid" id="servicesGrid">
            <!-- Services will be populated here -->
        </div>
        
        <!-- Alerts -->
        <div class="alerts-section" id="alertsSection" style="display: none;">
            <h3>Active Alerts</h3>
            <div id="alertsList">
                <!-- Alerts will be populated here -->
            </div>
        </div>
        
        <div class="timestamp" id="lastUpdate">
            Last updated: --
        </div>
    </div>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connectionStatus = document.getElementById('connectionStatus');
        
        ws.onopen = function(event) {
            connectionStatus.textContent = 'Connected';
            connectionStatus.className = 'connection-status connected';
        };
        
        ws.onclose = function(event) {
            connectionStatus.textContent = 'Disconnected';
            connectionStatus.className = 'connection-status disconnected';
        };
        
        ws.onerror = function(event) {
            connectionStatus.textContent = 'Connection Error';
            connectionStatus.className = 'connection-status disconnected';
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        
        function updateDashboard(data) {
            // Update system metrics
            if (data.current_metrics) {
                const metrics = data.current_metrics;
                
                document.getElementById('cpuUsage').textContent = metrics.cpu_usage.toFixed(1) + '%';
                document.getElementById('memoryUsage').textContent = metrics.memory_usage.toFixed(1) + '%';
                document.getElementById('diskUsage').textContent = metrics.disk_usage.toFixed(1) + '%';
                
                updateProgressBar('cpuProgress', metrics.cpu_usage);
                updateProgressBar('memoryProgress', metrics.memory_usage);
                updateProgressBar('diskProgress', metrics.disk_usage);
            }
            
            // Update service count
            if (data.system_overview) {
                const overview = data.system_overview;
                document.getElementById('activeServices').textContent = 
                    `${overview.services_healthy} / ${overview.total_services}`;
            }
            
            // Update services
            if (data.service_status) {
                updateServices(data.service_status);
            }
            
            // Update alerts
            if (data.active_alerts) {
                updateAlerts(data.active_alerts);
            }
            
            // Update timestamp
            document.getElementById('lastUpdate').textContent = 
                'Last updated: ' + new Date().toLocaleTimeString();
        }
        
        function updateProgressBar(elementId, value) {
            const progressBar = document.getElementById(elementId);
            progressBar.style.width = value + '%';
            
            // Set color based on value
            if (value < 70) {
                progressBar.className = 'progress-fill progress-normal';
            } else if (value < 85) {
                progressBar.className = 'progress-fill progress-warning';
            } else {
                progressBar.className = 'progress-fill progress-danger';
            }
        }
        
        function updateServices(services) {
            const servicesGrid = document.getElementById('servicesGrid');
            servicesGrid.innerHTML = '';
            
            for (const [serviceName, serviceData] of Object.entries(services)) {
                const serviceCard = document.createElement('div');
                serviceCard.className = 'service-card';
                
                const statusClass = serviceData.status === 'healthy' ? 'status-healthy' : 
                                  serviceData.status === 'unhealthy' ? 'status-unhealthy' : 'status-warning';
                
                serviceCard.innerHTML = `
                    <div class="service-header">
                        <span class="status-indicator ${statusClass}"></span>
                        <div>
                            <div class="service-name">${serviceName}</div>
                            <div class="service-response-time">
                                Response: ${serviceData.response_time.toFixed(0)}ms
                                ${serviceData.error_message ? '- ' + serviceData.error_message : ''}
                            </div>
                        </div>
                    </div>
                `;
                
                servicesGrid.appendChild(serviceCard);
            }
        }
        
        function updateAlerts(alerts) {
            const alertsSection = document.getElementById('alertsSection');
            const alertsList = document.getElementById('alertsList');
            
            if (alerts.length === 0) {
                alertsSection.style.display = 'none';
                return;
            }
            
            alertsSection.style.display = 'block';
            alertsList.innerHTML = '';
            
            alerts.forEach(alert => {
                const alertItem = document.createElement('div');
                alertItem.className = 'alert-item';
                
                alertItem.innerHTML = `
                    <div class="alert-severity alert-${alert.severity}">${alert.severity}</div>
                    <div>${alert.message}</div>
                    <div style="font-size: 0.8rem; color: #a0a0a0; margin-top: 0.5rem;">
                        ${new Date(alert.timestamp).toLocaleString()}
                    </div>
                `;
                
                alertsList.appendChild(alertItem);
            });
        }
    </script>
</body>
</html>
    """
    return html_content

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send monitoring data every 5 seconds
            await asyncio.sleep(5)
            
            # Get latest monitoring data
            try:
                report = monitor.generate_monitoring_report()
                await manager.broadcast(report)
            except Exception as e:
                logger.error(f"Error generating monitoring data: {e}")
                await manager.broadcast({
                    "error": "Failed to generate monitoring data",
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_system_status():
    """Get current system status"""
    try:
        report = monitor.generate_monitoring_report()
        return report
    except Exception as e:
        logger.error(f"Error generating system status: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/api/metrics")
async def get_metrics_history():
    """Get metrics history"""
    try:
        metrics_data = []
        for metric in monitor.metrics_history[-100:]:  # Last 100 entries
            metrics_data.append(metric.to_dict())
        
        return {
            "metrics": metrics_data,
            "count": len(metrics_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/api/services")
async def get_services_status():
    """Get services status"""
    try:
        service_statuses = monitor.check_all_services()
        return {
            "services": {name: status.to_dict() for name, status in service_statuses.items()},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting services status: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    """Health check endpoint for the monitoring service itself"""
    return {
        "status": "healthy",
        "service": "PROJECT SENTINEL - Monitoring Dashboard",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

async def background_monitoring():
    """Background task to collect monitoring data"""
    while True:
        try:
            monitor.run_monitoring_cycle()
            await asyncio.sleep(30)  # Collect data every 30 seconds
        except Exception as e:
            logger.error(f"Background monitoring error: {e}")
            await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    """Start background monitoring when the app starts"""
    asyncio.create_task(background_monitoring())
    logger.info("PROJECT SENTINEL Monitoring Dashboard started")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8006,
        log_level="info"
    )
