#!/usr/bin/env python3
"""
Web Monitor for CryptoMiner Pro V30 Terminal Application
Lightweight web interface for monitoring terminal mining
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    import uvicorn
except ImportError:
    print("⚠️ Web monitoring dependencies not found. Install with: pip install fastapi uvicorn websockets")
    FastAPI = None

logger = logging.getLogger(__name__)

class WebMonitor:
    def __init__(self, mining_engine, port=3333):
        if FastAPI is None:
            raise ImportError("FastAPI not available. Install with: pip install fastapi uvicorn")
            
        self.mining_engine = mining_engine
        self.port = port
        self.app = FastAPI(title="CryptoMiner Pro V30 Monitor")
        self.active_connections = []
        self.server_thread = None
        self.running = False
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self.get_dashboard_html()
            
        @self.app.get("/api/status")
        async def get_status():
            if self.mining_engine:
                status = self.mining_engine.get_mining_status()
                return {
                    "success": True,
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                }
            return {"success": False, "error": "Mining engine not available"}
            
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    if self.mining_engine:
                        status = self.mining_engine.get_mining_status()
                        await websocket.send_json({
                            "type": "mining_status",
                            "data": status,
                            "timestamp": datetime.now().isoformat()
                        })
                    await asyncio.sleep(2)  # Update every 2 seconds
                    
            except WebSocketDisconnect:
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
                    
    def get_dashboard_html(self):
        """Generate the monitoring dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoMiner Pro V30 - Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: #fff;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card h3 {
            font-size: 1.4rem;
            margin-bottom: 15px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-connected {
            background-color: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        .status-disconnected {
            background-color: #f44336;
        }
        
        .status-error {
            background-color: #ff9800;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 25px;
            background: rgba(0, 0, 0, 0.7);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .mining-controls {
            text-align: center;
            margin-top: 30px;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        .btn.stop {
            background: linear-gradient(45deg, #f44336, #d32f2f);
        }
        
        .log-section {
            margin-top: 30px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 20px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .log-entry {
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            margin-bottom: 5px;
            padding: 5px;
            border-left: 3px solid #4CAF50;
            padding-left: 10px;
            opacity: 0.9;
        }
        
        .error-message {
            background: rgba(244, 67, 54, 0.2);
            border: 1px solid #f44336;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CryptoMiner Pro V30</h1>
            <div class="subtitle">Terminal Mining Monitor</div>
        </div>
        
        <div class="connection-status" id="connectionStatus">
            <div class="status-indicator status-disconnected" id="statusIndicator"></div>
            <span id="statusText">Connecting...</span>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>⚡ Hashrate</h3>
                <div class="stat-value" id="hashrate">0 H/s</div>
                <div class="stat-label">Current mining speed</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="hashrateProgress" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>🖥️ System</h3>
                <div class="stat-value" id="cpuUsage">0%</div>
                <div class="stat-label">CPU Usage</div>
                <div style="margin-top: 10px;">
                    <div style="font-size: 1.2rem;">🌡️ <span id="temperature">0°C</span></div>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>📊 Mining Stats</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 1rem;">
                    <div>✅ Accepted: <span id="accepted">0</span></div>
                    <div>❌ Rejected: <span id="rejected">0</span></div>
                    <div>🎯 Efficiency: <span id="efficiency">0%</span></div>
                    <div>🧵 Threads: <span id="threads">0</span></div>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>⏱️ Runtime</h3>
                <div class="stat-value" id="runtime">00:00:00</div>
                <div class="stat-label">Mining duration</div>
                <div style="margin-top: 10px; font-size: 1rem;">
                    <div>🔗 Status: <span id="miningStatus">Stopped</span></div>
                </div>
            </div>
        </div>
        
        <div class="log-section">
            <h3 style="margin-bottom: 15px;">📋 Recent Activity</h3>
            <div id="logContainer">
                <div class="log-entry">[INFO] Web monitor initialized</div>
                <div class="log-entry">[INFO] Connecting to mining engine...</div>
            </div>
        </div>
    </div>

    <script>
        let ws;
        let maxHashrate = 1000; // Dynamic max for progress bar
        let startTime;
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                updateConnectionStatus('connected');
                addLog('[INFO] Connected to mining engine');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'mining_status') {
                    updateStats(data.data);
                }
            };
            
            ws.onclose = function() {
                updateConnectionStatus('disconnected');
                addLog('[WARN] Connection lost. Attempting to reconnect...');
                setTimeout(connect, 3000);
            };
            
            ws.onerror = function(error) {
                updateConnectionStatus('error');
                addLog('[ERROR] WebSocket error occurred');
            };
        }
        
        function updateConnectionStatus(status) {
            const indicator = document.getElementById('statusIndicator');
            const text = document.getElementById('statusText');
            
            indicator.className = 'status-indicator status-' + status;
            
            switch(status) {
                case 'connected':
                    text.textContent = 'Connected';
                    break;
                case 'disconnected':
                    text.textContent = 'Disconnected';
                    break;
                case 'error':
                    text.textContent = 'Error';
                    break;
            }
        }
        
        function updateStats(stats) {
            // Update hashrate
            const hashrate = stats.hashrate || 0;
            document.getElementById('hashrate').textContent = formatHashrate(hashrate);
            
            // Update progress bar
            if (hashrate > maxHashrate) maxHashrate = hashrate;
            const hashratePercent = maxHashrate > 0 ? (hashrate / maxHashrate) * 100 : 0;
            document.getElementById('hashrateProgress').style.width = hashratePercent + '%';
            
            // Update system stats
            document.getElementById('cpuUsage').textContent = (stats.cpu_usage || 0).toFixed(1) + '%';
            document.getElementById('temperature').textContent = (stats.temperature || 0).toFixed(1) + '°C';
            
            // Update mining stats
            const accepted = stats.accepted_shares || 0;
            const rejected = stats.rejected_shares || 0;
            const efficiency = (accepted + rejected) > 0 ? ((accepted / (accepted + rejected)) * 100).toFixed(1) : '0';
            
            document.getElementById('accepted').textContent = accepted;
            document.getElementById('rejected').textContent = rejected;
            document.getElementById('efficiency').textContent = efficiency + '%';
            document.getElementById('threads').textContent = stats.active_threads || 0;
            
            // Update runtime and status
            document.getElementById('miningStatus').textContent = stats.is_mining ? 'Active' : 'Stopped';
            
            if (stats.is_mining && !startTime) {
                startTime = new Date();
            } else if (!stats.is_mining) {
                startTime = null;
            }
            
            if (startTime) {
                const runtime = Math.floor((new Date() - startTime) / 1000);
                document.getElementById('runtime').textContent = formatTime(runtime);
            } else {
                document.getElementById('runtime').textContent = '00:00:00';
            }
        }
        
        function formatHashrate(hashrate) {
            if (hashrate > 1000000) {
                return (hashrate / 1000000).toFixed(2) + ' MH/s';
            } else if (hashrate > 1000) {
                return (hashrate / 1000).toFixed(2) + ' KH/s';
            } else {
                return hashrate.toFixed(2) + ' H/s';
            }
        }
        
        function formatTime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        function addLog(message) {
            const container = document.getElementById('logContainer');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.textContent = `[${timestamp}] ${message}`;
            
            container.appendChild(logEntry);
            
            // Keep only last 20 entries
            while (container.children.length > 20) {
                container.removeChild(container.firstChild);
            }
            
            // Auto-scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        // Initialize connection
        connect();
        
        // Update time every second
        setInterval(() => {
            if (startTime) {
                const runtime = Math.floor((new Date() - startTime) / 1000);
                document.getElementById('runtime').textContent = formatTime(runtime);
            }
        }, 1000);
    </script>
</body>
</html>
        """
        
    def start(self):
        """Start the web monitor server"""
        if self.running:
            logger.warning("Web monitor is already running")
            return
            
        def run_server():
            try:
                uvicorn.run(
                    self.app,
                    host="0.0.0.0",
                    port=self.port,
                    log_level="error",  # Minimize uvicorn output
                    access_log=False
                )
            except Exception as e:
                logger.error(f"Web monitor server error: {e}")
                
        self.running = True
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Give server time to start
        time.sleep(2)
        
    def stop(self):
        """Stop the web monitor server"""
        self.running = False
        
        # Close all WebSocket connections
        for connection in self.active_connections:
            try:
                asyncio.create_task(connection.close())
            except Exception:
                pass
                
        self.active_connections.clear()
        logger.info("Web monitor stopped")
        
    async def broadcast_message(self, message):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
            
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except Exception:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)