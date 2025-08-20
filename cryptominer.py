#!/usr/bin/env python3
"""
🚀 CryptoMiner Pro V30 🚀
Enterprise-scale distributed mining platform
Consolidated terminal-based mining application with optional web monitoring
"""

import argparse
import asyncio
import signal
import sys
import os
import time
import threading
import http.server
import socketserver
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import consolidated modules
from config import config
from constants import APP_NAME, APP_VERSION, BANNER, SUPPORTED_COINS
from utils import format_uptime

# Load configuration from mining_config.env if it exists
config_file = Path("mining_config.env")
if config_file.exists():
    load_dotenv(config_file)
    print(f"📁 Loaded configuration from {config_file}")
else:
    print("📁 No mining_config.env found, using command line arguments or defaults")

# Configure logging using centralized config
config.setup_logging()
import logging
logger = logging.getLogger(__name__)

# Import mining components
try:
    from mining_engine import MiningEngine
    from ai_optimizer import AIOptimizer
except ImportError as e:
    logger.error(f"Failed to import mining components: {e}")
    sys.exit(1)

class CryptoMinerPro:
    def __init__(self):
        self.mining_engine = None
        self.ai_optimizer = None
        self.web_server_task = None
        self.web_server_thread = None
        self.backend_process = None
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def create_web_dashboard(self):
        """Create the HTML web dashboard"""
        dashboard_dir = Path("web-dashboard")
        dashboard_dir.mkdir(exist_ok=True)
        
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 CryptoMiner Pro V30 Dashboard</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            min-width: 120px;
        }
        
        .btn-start {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
        }
        
        .btn-start:hover {
            background: linear-gradient(135deg, #218838, #1ea080);
            transform: translateY(-2px);
        }
        
        .btn-stop {
            background: linear-gradient(135deg, #dc3545, #fd7e14);
            color: white;
        }
        
        .btn-stop:hover {
            background: linear-gradient(135deg, #c82333, #e8590c);
            transform: translateY(-2px);
        }
        
        .btn-restart {
            background: linear-gradient(135deg, #17a2b8, #6f42c1);
            color: white;
        }
        
        .btn-restart:hover {
            background: linear-gradient(135deg, #138496, #5a2d91);
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .card h3 {
            margin-top: 0;
            color: #61dafb;
            font-size: 1.3em;
            border-bottom: 2px solid #61dafb;
            padding-bottom: 10px;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat:last-child {
            border-bottom: none;
        }
        
        .value {
            font-weight: bold;
            color: #00ff88;
        }
        
        .status-connected {
            color: #00ff88;
        }
        
        .status-disconnected {
            color: #ff4444;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #61dafb);
            transition: width 0.3s ease;
        }
        
        .error {
            background: rgba(255, 68, 68, 0.2);
            border: 1px solid #ff4444;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .success {
            background: rgba(40, 167, 69, 0.2);
            border: 1px solid #28a745;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .timestamp {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }
        
        .config-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .config-input {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 8px 0;
        }
        
        .config-input input, .config-input select {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 5px;
            padding: 8px;
            color: white;
            width: 60%;
        }
        
        .config-input input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CryptoMiner Pro V30</h1>
            <p>Enterprise Mining Dashboard</p>
        </div>
        
        <!-- Control Buttons -->
        <div class="controls">
            <button id="start-btn" class="btn btn-start" onclick="startMining()">▶️ Start Mining</button>
            <button id="stop-btn" class="btn btn-stop" onclick="stopMining()">⏹️ Stop Mining</button>
            <button id="restart-btn" class="btn btn-restart" onclick="restartMining()">🔄 Restart Mining</button>
        </div>
        
        <div id="error-message" class="error" style="display: none;">
            ❌ Cannot connect to mining API. Make sure the backend is running on port 8001.
        </div>
        
        <div id="success-message" class="success" style="display: none;">
            ✅ Command executed successfully
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>⚡ Mining Status</h3>
                <div class="stat">
                    <span>Hashrate:</span>
                    <span class="value" id="hashrate">0 H/s</span>
                </div>
                <div class="stat">
                    <span>Threads:</span>
                    <span class="value" id="threads">0</span>
                </div>
                <div class="stat">
                    <span>Intensity:</span>
                    <span class="value" id="intensity">0%</span>
                </div>
                <div class="stat">
                    <span>Coin:</span>
                    <span class="value" id="coin">-</span>
                </div>
                <div class="stat">
                    <span>Pool:</span>
                    <span class="value" id="pool-status">❌ Disconnected</span>
                </div>
                <div class="stat">
                    <span>Difficulty:</span>
                    <span class="value" id="difficulty">0</span>
                </div>
                
                <!-- Quick Configuration Section -->
                <div class="config-section">
                    <h4 style="margin: 0 0 10px 0; color: #61dafb;">⚙️ Quick Config</h4>
                    <div class="config-input">
                        <span>Pool:</span>
                        <input type="text" id="config-pool" placeholder="ltc.luckymonster.pro:4112">
                    </div>
                    <div class="config-input">
                        <span>Threads:</span>
                        <input type="number" id="config-threads" placeholder="8" min="1" max="32">
                    </div>
                    <div class="config-input">
                        <span>Intensity:</span>
                        <input type="number" id="config-intensity" placeholder="80" min="1" max="100">
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 Share Statistics</h3>
                <div class="stat">
                    <span>Accepted:</span>
                    <span class="value" id="accepted-shares">0</span>
                </div>
                <div class="stat">
                    <span>Rejected:</span>
                    <span class="value" id="rejected-shares">0</span>
                </div>
                <div class="stat">
                    <span>Total:</span>
                    <span class="value" id="total-shares">0</span>
                </div>
                <div class="stat">
                    <span>Acceptance Rate:</span>
                    <span class="value" id="acceptance-rate">0%</span>
                </div>
                <div class="stat">
                    <span>Uptime:</span>
                    <span class="value" id="uptime">0h 0m 0s</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 AI Optimization</h3>
                <div class="stat">
                    <span>AI Learning:</span>
                    <span class="value" id="ai-learning">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="ai-learning-bar" style="width: 0%"></div>
                </div>
                <div class="stat">
                    <span>AI Optimization:</span>
                    <span class="value" id="ai-optimization">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="ai-optimization-bar" style="width: 0%"></div>
                </div>
            </div>
        </div>
        
        <div class="timestamp" id="last-update">
            Last updated: Never
        </div>
    </div>

    <script>
        let isConnected = false;
        let isMining = false;
        
        function formatHashrate(hashrate) {
            if (hashrate >= 1000000) return `${(hashrate / 1000000).toFixed(2)} MH/s`;
            if (hashrate >= 1000) return `${(hashrate / 1000).toFixed(2)} KH/s`;
            return `${hashrate.toFixed(2)} H/s`;
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours}h ${minutes}m ${secs}s`;
        }
        
        function showMessage(message, isError = false) {
            const errorEl = document.getElementById('error-message');
            const successEl = document.getElementById('success-message');
            
            if (isError) {
                errorEl.innerHTML = `❌ ${message}`;
                errorEl.style.display = 'block';
                successEl.style.display = 'none';
            } else {
                successEl.innerHTML = `✅ ${message}`;
                successEl.style.display = 'block';
                errorEl.style.display = 'none';
            }
            
            setTimeout(() => {
                errorEl.style.display = 'none';
                successEl.style.display = 'none';
            }, 5000);
        }
        
        function updateButtonStates() {
            const startBtn = document.getElementById('start-btn');
            const stopBtn = document.getElementById('stop-btn');
            const restartBtn = document.getElementById('restart-btn');
            
            if (isMining) {
                startBtn.disabled = true;
                stopBtn.disabled = false;
                restartBtn.disabled = false;
            } else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
                restartBtn.disabled = true;
            }
        }
        
        async function sendControlCommand(action, config = null) {
            try {
                const payload = { action: action };
                if (config) {
                    payload.config = config;
                }
                
                const response = await fetch('http://localhost:8001/api/mining/control', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const result = await response.json();
                showMessage(result.message || `${action} command sent successfully`);
                
                // Update UI based on action
                if (action === 'start') {
                    isMining = true;
                } else if (action === 'stop') {
                    isMining = false;
                }
                updateButtonStates();
                
            } catch (error) {
                showMessage(`Failed to ${action} mining: ${error.message}`, true);
            }
        }
        
        async function startMining() {
            const pool = document.getElementById('config-pool').value || 'ltc.luckymonster.pro:4112';
            const threads = parseInt(document.getElementById('config-threads').value) || 8;
            const intensity = parseInt(document.getElementById('config-intensity').value) || 80;
            
            const config = {
                pool: pool,
                threads: threads,
                intensity: intensity
            };
            
            await sendControlCommand('start', config);
        }
        
        async function stopMining() {
            await sendControlCommand('stop');
        }
        
        async function restartMining() {
            await sendControlCommand('restart');
        }
        
        async function fetchMiningStats() {
            try {
                const response = await fetch('http://localhost:8001/api/mining/stats');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const stats = await response.json();
                
                document.getElementById('hashrate').textContent = formatHashrate(stats.hashrate || 0);
                document.getElementById('threads').textContent = stats.threads || 0;
                document.getElementById('intensity').textContent = `${stats.intensity || 0}%`;
                document.getElementById('coin').textContent = stats.coin || 'LTC';
                document.getElementById('difficulty').textContent = stats.difficulty || 0;
                
                const poolStatus = document.getElementById('pool-status');
                if (stats.pool_connected) {
                    poolStatus.textContent = '✅ Connected';
                    poolStatus.className = 'value status-connected';
                    isMining = true;
                } else {
                    poolStatus.textContent = '❌ Disconnected';
                    poolStatus.className = 'value status-disconnected';
                    isMining = false;
                }
                
                updateButtonStates();
                
                const accepted = stats.accepted_shares || 0;
                const rejected = stats.rejected_shares || 0;
                const total = accepted + rejected;
                const acceptanceRate = total > 0 ? ((accepted / total) * 100).toFixed(1) : 0;
                
                document.getElementById('accepted-shares').textContent = accepted;
                document.getElementById('rejected-shares').textContent = rejected;
                document.getElementById('total-shares').textContent = total;
                document.getElementById('acceptance-rate').textContent = `${acceptanceRate}%`;
                document.getElementById('uptime').textContent = formatUptime(stats.uptime || 0);
                
                const aiLearning = stats.ai_learning || 0;
                const aiOptimization = stats.ai_optimization || 0;
                
                document.getElementById('ai-learning').textContent = `${aiLearning.toFixed(1)}%`;
                document.getElementById('ai-optimization').textContent = `${aiOptimization.toFixed(1)}%`;
                document.getElementById('ai-learning-bar').style.width = `${Math.min(aiLearning, 100)}%`;
                document.getElementById('ai-optimization-bar').style.width = `${Math.min(aiOptimization, 100)}%`;
                
                document.getElementById('last-update').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
                
                document.getElementById('error-message').style.display = 'none';
                isConnected = true;
                
            } catch (error) {
                console.error('Failed to fetch mining stats:', error);
                document.getElementById('error-message').style.display = 'block';
                isConnected = false;
                isMining = false;
                updateButtonStates();
            }
        }
        
        fetchMiningStats();
        setInterval(fetchMiningStats, 5000);
        
        setInterval(() => {
            document.title = isConnected ? '🚀 CryptoMiner Pro V30 - Connected' : '❌ CryptoMiner Pro V30 - Disconnected';
        }, 1000);
        
        // Initialize button states
        updateButtonStates();
    </script>
</body>
</html>'''
        
        dashboard_file = dashboard_dir / "index.html"
        dashboard_file.write_text(dashboard_html)
        logger.info(f"📄 Created web dashboard: {dashboard_file}")
        return dashboard_dir
    
    def start_web_dashboard(self, dashboard_dir, port=3000):
        """Start the web dashboard server in a separate thread"""
        def run_server():
            try:
                os.chdir(dashboard_dir)
                handler = http.server.SimpleHTTPRequestHandler
                with socketserver.TCPServer(("", port), handler) as httpd:
                    logger.info(f"🌐 Web dashboard started: http://localhost:{port}")
                    httpd.serve_forever()
            except Exception as e:
                logger.error(f"Web dashboard server error: {e}")
        
        self.web_server_thread = threading.Thread(target=run_server, daemon=True)
        self.web_server_thread.start()
    
    def start_backend_server(self):
        """Start the FastAPI backend server"""
        try:
            import subprocess
            backend_cmd = [
                sys.executable, "-m", "uvicorn", 
                "backend.server:app", 
                "--host", "0.0.0.0", 
                "--port", "8001",
                "--reload"
            ]
            self.backend_process = subprocess.Popen(
                backend_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            logger.info("🔧 Backend API server started on port 8001")
        except Exception as e:
            logger.error(f"Failed to start backend server: {e}")

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C and termination signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        if self.running:
            # Create shutdown task in the current event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.shutdown())
                else:
                    asyncio.run(self.shutdown())
            except RuntimeError:
                # No event loop running, create new one
                asyncio.run(self.shutdown())

    async def shutdown(self):
        """Gracefully shutdown all mining components"""
        logger.info("🛑 Shutting down CryptoMiner Pro V30...")
        self.running = False
        self.shutdown_event.set()
        
        # Cancel all running tasks
        try:
            # Get all running tasks except current one
            current_task = asyncio.current_task()
            tasks = [task for task in asyncio.all_tasks() if task is not current_task and not task.done()]
            
            if tasks:
                logger.info(f"Cancelling {len(tasks)} running tasks...")
                for task in tasks:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                try:
                    await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Some tasks did not shutdown gracefully within timeout")
        
        except Exception as e:
            logger.error(f"Error during task cleanup: {e}")
        
        # Stop mining engine
        if self.mining_engine:
            logger.info("Stopping mining engine...")
            try:
                await asyncio.wait_for(self.mining_engine.stop(), timeout=3.0)
            except asyncio.TimeoutError:
                logger.warning("Mining engine shutdown timed out")
            except Exception as e:
                logger.error(f"Error stopping mining engine: {e}")
            
        # Stop AI optimizer
        if self.ai_optimizer:
            logger.info("Stopping AI optimizer...")
            try:
                self.ai_optimizer.stop()
            except Exception as e:
                logger.error(f"Error stopping AI optimizer: {e}")
            
        # Stop web server
        if self.web_server_task and not self.web_server_task.done():
            logger.info("Stopping web monitoring server...")
            try:
                self.web_server_task.cancel()
                await asyncio.wait_for(self.web_server_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            except Exception as e:
                logger.error(f"Error stopping web server: {e}")
        
        # Force close any remaining connections
        try:
            # Close any open sockets or connections
            if hasattr(self, 'mining_engine') and self.mining_engine and hasattr(self.mining_engine, 'miners'):
                for miner in self.mining_engine.miners:
                    if hasattr(miner, 'socket') and miner.socket:
                        try:
                            miner.socket.close()
                        except:
                            pass
        except Exception as e:
            logger.error(f"Error during connection cleanup: {e}")
        
        logger.info("✅ CryptoMiner Pro V30 shutdown complete")
        
        # Force exit if we're in signal handler context
        try:
            loop = asyncio.get_running_loop()
            loop.stop()
        except RuntimeError:
            pass

    def print_banner(self):
        """Display the application banner"""
        print(BANNER)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def list_coins(self):
        """List available coins for mining"""
        print("\n📋 Available Coins:")
        print("=" * 50)
        for symbol, info in SUPPORTED_COINS.items():
            print(f"  {symbol:<6} - {info['description']}")
        print()

    async def setup_interactive(self):
        """Interactive setup wizard"""
        print("\n🔧 CryptoMiner Pro V30 - Interactive Setup")
        print("=" * 50)
        
        # Get coin selection
        self.list_coins()
        coin = input("Enter coin symbol (e.g., LTC): ").upper().strip()
        
        # Get wallet address
        wallet = input("Enter your wallet address: ").strip()
        
        # Get pool information
        pool = input("Enter pool URL (e.g., stratum+tcp://pool.example.com:4444): ").strip()
        
        # Get optional password
        password = input("Enter pool password (optional, press Enter to skip): ").strip()
        if not password:
            password = None
            
        # Get mining intensity
        intensity = input("Enter mining intensity 1-100% (default: 80): ").strip()
        if not intensity:
            intensity = 80
        else:
            try:
                intensity = max(1, min(100, int(intensity)))
            except ValueError:
                intensity = 80
                
        # Get thread count
        threads = input("Enter number of threads (default: auto): ").strip()
        if not threads:
            threads = None
        else:
            try:
                threads = max(1, int(threads))
            except ValueError:
                threads = None
        
        # Save configuration
        config = f"""# CryptoMiner Pro V30 Configuration
# Generated by interactive setup on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

COIN={coin}
WALLET={wallet}
POOL={pool}
PASSWORD={password or ''}
INTENSITY={intensity}
THREADS={threads or 'auto'}
WEB_PORT=8001
WEB_ENABLED=true
AI_ENABLED=true
"""
        
        with open('mining_config.env', 'w') as f:
            f.write(config)
            
        print(f"\n✅ Configuration saved to mining_config.env")
        
        # Ask if user wants to start mining
        start_now = input("\nStart mining now? (y/n): ").lower().strip()
        if start_now in ['y', 'yes']:
            await self.start_mining(coin, wallet, pool, password, intensity, threads, proxy_mode=False)

    async def start_mining(self, coin, wallet, pool, password=None, intensity=80, threads=None, proxy_mode=False):
        """Start the mining operation"""
        self.running = True
        
        logger.info(f"🚀 Starting CryptoMiner Pro V30")
        logger.info(f"Coin: {coin}")
        logger.info(f"Wallet: {wallet}")
        logger.info(f"Pool: {pool}")
        logger.info(f"Intensity: {intensity}%")
        logger.info(f"Threads: {threads or 'auto'}")
        logger.info(f"Connection Mode: {'Proxy (Single Connection)' if proxy_mode else 'Direct (Multiple Connections)'}")
        
        try:
            if proxy_mode:
                logger.info("🔄 Initializing proxy connection manager")
                from proxy_mining_engine import ProxyMiningEngine
                
                # Initialize proxy mining engine  
                self.mining_engine = ProxyMiningEngine(
                    coin=coin,
                    wallet=wallet,
                    pool_url=pool,
                    password=password or "x",
                    intensity=intensity
                )
                
                # Set thread count if specified
                if threads:
                    self.mining_engine.set_thread_count(threads)
                
            else:
                logger.info("🔗 Initializing direct connection mining engine")
                from mining_engine import MiningEngine
                
                # Initialize AI optimizer
                self.ai_optimizer = AIOptimizer()
                
                # Initialize traditional mining engine
                self.mining_engine = MiningEngine(
                    coin=coin,
                    wallet=wallet, 
                    pool=pool,
                    password=password,
                    intensity=intensity,
                    ai_optimizer=self.ai_optimizer
                )
                
                # Set thread count if specified
                if threads:
                    self.mining_engine.set_thread_count(threads)
            
            # Start web dashboard
            dashboard_dir = self.create_web_dashboard()
            self.start_web_dashboard(dashboard_dir)
            
            # Start web monitoring server
            self.web_server_task = asyncio.create_task(self.start_web_server())
            
            # Start mining in background task
            mining_task = asyncio.create_task(self.mining_engine.start())
            
            # Run both tasks concurrently and wait for shutdown signal
            try:
                while self.running:
                    # Check if mining engine is still running
                    if mining_task.done():
                        logger.warning("Mining engine stopped unexpectedly")
                        break
                    
                    # Check if web monitoring is still running
                    if self.web_server_task.done():
                        logger.warning("Web monitoring stopped unexpectedly")
                        # Restart web monitoring
                        self.web_server_task = asyncio.create_task(self.start_web_server())
                    
                    # Wait for shutdown signal or brief sleep
                    try:
                        await asyncio.wait_for(self.shutdown_event.wait(), timeout=1.0)
                        break  # Shutdown signal received
                    except asyncio.TimeoutError:
                        continue  # Normal operation, continue loop
                        
            except asyncio.CancelledError:
                logger.info("Mining tasks cancelled")
            except Exception as e:
                logger.error(f"Task execution error: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Mining error: {e}")
        finally:
            # Ensure clean shutdown
            if self.running:
                await self.shutdown()

    async def start_web_server(self):
        """Start the web monitoring server and data updates"""
        try:
            logger.info("🌐 Web monitoring integration started")
            
            # Start periodic data updates to backend API
            while self.running:
                try:
                    logger.info(f"⏰ Web monitoring loop iteration - running: {self.running}")
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
                    if not self.running:
                        break
                    
                    # Get current mining stats
                    if self.mining_engine:
                        stats = self.mining_engine.get_stats()
                        logger.info(f"📊 Current mining stats: {stats}")
                        
                        # Send stats to backend API
                        await self._update_backend_stats(stats)
                    else:
                        logger.info("⚠️ Mining engine not available for stats")
                    
                except Exception as e:
                    logger.error(f"Web monitoring update error: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to start web monitoring: {e}")

    async def _update_backend_stats(self, stats):
        """Update backend API with current mining statistics"""
        try:
            import aiohttp
            
            backend_url = "http://localhost:8001/api/mining/update-stats"
            
            # Prepare stats data for API
            api_stats = {
                "hashrate": float(stats.get('hashrate', 0)),
                "threads": int(stats.get('thread_count', 0)),
                "intensity": int(stats.get('intensity', 80)),
                "coin": str(stats.get('coin', 'LTC')),
                "pool_connected": bool(stats.get('pool_connected', False)),
                "accepted_shares": int(stats.get('accepted_shares', 0)),
                "rejected_shares": int(stats.get('rejected_shares', 0)),
                "uptime": float(time.time() - stats.get('uptime', time.time())),
                "difficulty": float(stats.get('difficulty', 1)),
                "ai_learning": float(stats.get('ai_stats', {}).get('learning_progress', 0)) if stats.get('ai_stats') else 0,
                "ai_optimization": float(stats.get('ai_stats', {}).get('optimization_progress', 0)) if stats.get('ai_stats') else 0
            }
            
            logger.info(f"📊 Sending stats to local backend API: {api_stats}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(backend_url, json=api_stats, timeout=5) as response:
                    if response.status == 200:
                        logger.info("✅ Stats updated to web dashboard successfully")
                    else:
                        logger.warning(f"❌ Web API update failed: {response.status}")
                        
        except ImportError:
            logger.warning("aiohttp not available for web monitoring updates")
        except Exception as e:
            logger.error(f"Web stats update error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Enterprise Mining Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cryptominer.py --setup                    # Interactive setup
  python3 cryptominer.py --list-coins              # Show available coins
  python3 cryptominer.py --coin LTC --wallet LTC_ADDRESS --pool stratum+tcp://pool.example.com:4444
  python3 cryptominer.py --coin LTC --wallet LTC_ADDRESS --pool stratum+tcp://pool.example.com:4444 --password worker1 --intensity 90 --threads 8

Configuration File:
  Create mining_config.env with your settings:
    COIN=LTC
    WALLET=your_wallet_address
    POOL=stratum+tcp://pool.example.com:4444
    PASSWORD=worker1
    INTENSITY=80
    THREADS=4
        """
    )
    
    # Get defaults from centralized configuration
    cfg = config.to_dict()
    
    parser.add_argument('--setup', action='store_true', help='Run interactive setup wizard')
    parser.add_argument('--list-coins', action='store_true', help='List available coins')
    parser.add_argument('--coin', default=cfg.get('coin'), help='Coin to mine (e.g., LTC, DOGE)')
    parser.add_argument('--wallet', default=cfg.get('wallet'), help='Wallet address')
    parser.add_argument('--pool', default=cfg.get('pool'), help='Mining pool URL')
    parser.add_argument('--password', default=cfg.get('password'), help='Pool password (optional)')
    parser.add_argument('--intensity', type=int, default=cfg.get('intensity', 80), help=f'Mining intensity 1-100%% (default: {cfg.get("intensity", 80)})')
    parser.add_argument('--threads', type=int, default=cfg.get('threads'), help='Number of threads (default: auto)')
    parser.add_argument('--web-port', type=int, default=cfg.get('web_port', 8001), help=f'Web monitoring port (default: {cfg.get("web_port", 8001)})')
    parser.add_argument('--proxy-mode', action='store_true', help='Use proxy connection manager (single pool connection, multiple threads)')
    parser.add_argument('--config', help='Use specific config file (default: mining_config.env)')
    
    args = parser.parse_args()
    
    # Load custom config file if specified
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            load_dotenv(config_path)
            print(f"📁 Loaded custom configuration from {config_path}")
        else:
            print(f"❌ Config file not found: {config_path}")
            return 1
    
    # Create miner instance
    miner = CryptoMinerPro()
    
    # Show banner
    miner.print_banner()
    
    # Display current configuration if loaded from env
    if any([cfg.get('coin'), cfg.get('wallet'), cfg.get('pool')]):
        print("\n⚙️ Configuration loaded from file:")
        print(f"  Coin: {args.coin or 'Not set'}")
        print(f"  Wallet: {args.wallet or 'Not set'}")
        print(f"  Pool: {args.pool or 'Not set'}")
        print(f"  Intensity: {args.intensity}%")
        print(f"  Threads: {args.threads or 'auto'}")
        print()
    
    # Handle different modes
    if args.list_coins:
        miner.list_coins()
        return
        
    if args.setup:
        asyncio.run(miner.setup_interactive())
        return
        
    if args.coin and args.wallet and args.pool:
        # Direct mining mode
        asyncio.run(miner.start_mining(
            coin=args.coin,
            wallet=args.wallet,
            pool=args.pool,
            password=args.password,
            intensity=args.intensity,
            threads=args.threads,
            proxy_mode=args.proxy_mode
        ))
        return
    
    # No valid configuration found
    print("⚠️  Incomplete configuration!")
    print("\nOptions:")
    print("  1. Create mining_config.env file:")
    print("     cp mining_config.template mining_config.env")
    print("     # Edit mining_config.env with your settings")
    print("     python3 cryptominer.py")
    print()
    print("  2. Use interactive setup:")
    print("     python3 cryptominer.py --setup")
    print()
    print("  3. Use command line arguments:")
    print("     python3 cryptominer.py --coin LTC --wallet ADDRESS --pool POOL:PORT")
    print()
    print("For full help: python3 cryptominer.py --help")

if __name__ == "__main__":
    main()