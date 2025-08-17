#!/usr/bin/env python3
"""
CryptoMiner Pro V30 - Compact Terminal Mining Application
Enterprise-grade mining with optional web monitoring in a single file
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Import existing backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from mining_engine import EnterpriseScryptMiner, EnterpriseSystemDetector, CoinConfig
from ai_system import AISystemManager
from utils import get_coin_presets, validate_wallet_address

# Web monitoring imports (optional)
try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    import uvicorn
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mining.log')
    ]
)

logger = logging.getLogger(__name__)

class CompactMiner:
    def __init__(self):
        self.mining_engine = None
        self.ai_system = None
        self.web_app = None
        self.web_server = None
        self.config = {}
        self.running = False
        self.stats = {
            'start_time': None,
            'total_hashes': 0,
            'shares_submitted': 0,
            'last_hashrate': 0
        }
        self.web_connections = []
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown"""
        def signal_handler(sig, frame):
            print(f"\n🛑 Stopping mining...")
            self.stop_mining()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def print_banner(self):
        """Display banner"""
        print("""
╔══════════════════════════════════════════════════════════╗
║              🚀 CryptoMiner Pro V30 🚀                  ║
║           Compact Terminal Mining Application            ║
║                                                         ║
║  ⚡ Enterprise Mining Engine    🤖 AI Optimization     ║
║  🔗 Pool & Solo Support         📊 Web Monitoring      ║
╚══════════════════════════════════════════════════════════╝
        """)
        
    def load_config(self, config_file='mining_config.json'):
        """Load configuration"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"✅ Config loaded: {config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Config load failed: {e}")
                
    def save_config(self, config_file='mining_config.json'):
        """Save configuration"""
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"✅ Config saved: {config_file}")
        except Exception as e:
            logger.error(f"❌ Config save failed: {e}")
            
    def initialize_components(self):
        """Initialize mining components"""
        try:
            self.mining_engine = EnterpriseScryptMiner()
            self.ai_system = AISystemManager()
            logger.info("✅ Components initialized")
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
            
    def interactive_setup(self):
        """Interactive configuration"""
        print("\n🔧 Mining Setup")
        print("=" * 40)
        
        # Coin selection
        coin_presets = get_coin_presets()
        print("\n📈 Available Coins:")
        coins = list(coin_presets.items())
        for i, (_, coin_data) in enumerate(coins, 1):
            print(f"  {i}. {coin_data['name']} ({coin_data['symbol']})")
            
        while True:
            try:
                choice = int(input(f"\nSelect coin (1-{len(coins)}): ")) - 1
                coin_data = coins[choice][1]
                break
            except (ValueError, IndexError):
                print("❌ Invalid choice")
                
        self.config['coin'] = coin_data
        
        # Wallet address
        while True:
            wallet = input(f"\n💰 {coin_data['symbol']} wallet address: ").strip()
            if wallet:
                is_valid, message = validate_wallet_address(wallet, coin_data['symbol'])
                if is_valid:
                    self.config['wallet_address'] = wallet
                    print(f"✅ {message}")
                    break
                else:
                    print(f"❌ {message}")
                    
        # Mining mode
        print("\n⛏️ Mining Mode:")
        print("  1. Pool Mining")
        print("  2. Solo Mining")
        
        mode = input("Select (1-2): ").strip()
        if mode == "2":
            self.config['mode'] = 'solo'
        else:
            self.config['mode'] = 'pool'
            pool = input(f"🏊 Pool (stratum+tcp://pool:port): ").strip()
            if not pool:
                pool = f"stratum+tcp://{coin_data['symbol'].lower()}pool.org:3333"
            self.config['pool_address'] = pool
            
        # Threads
        max_threads = self.mining_engine.system_detector.system_capabilities.get('max_safe_threads', 8)
        threads = input(f"🧵 Threads (1-{max_threads}, default: auto): ").strip()
        self.config['threads'] = int(threads) if threads else max_threads // 2
        
        # Web monitoring
        web_port = input("📊 Web port (default: 3333, 0 to disable): ").strip()
        self.config['web_port'] = int(web_port) if web_port else 3333
        
        print(f"\n✅ Setup complete!")
        save = input("💾 Save config? (Y/n): ").strip().lower()
        if save != 'n':
            self.save_config()
            
    def start_mining(self):
        """Start mining"""
        if not self.config:
            print("❌ No configuration. Run with --setup")
            return False
            
        try:
            coin_config = CoinConfig(**self.config['coin'])
            success, message = self.mining_engine.start_mining(
                coin_config,
                self.config['wallet_address'],
                self.config['threads']
            )
            
            if success:
                self.running = True
                self.stats['start_time'] = datetime.now()
                print(f"✅ {message}")
                return True
            else:
                print(f"❌ {message}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mining error: {e}")
            return False
            
    def stop_mining(self):
        """Stop mining"""
        if self.mining_engine and self.running:
            success, message = self.mining_engine.stop_mining()
            self.running = False
            print(f"✅ Mining stopped")
            self.show_final_stats()
            
    def show_stats(self):
        """Display mining statistics"""
        if not self.running:
            return
            
        try:
            status = self.mining_engine.get_mining_status()
            stats = status.get('stats', {})
            
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Header
            print("╔══════════════════════════════════════════════════════════╗")
            print("║                  MINING STATISTICS                      ║")
            print("╠══════════════════════════════════════════════════════════╣")
            
            # Runtime
            if self.stats['start_time']:
                runtime = datetime.now() - self.stats['start_time']
                print(f"║  ⏱️  Runtime: {str(runtime).split('.')[0]:<44} ║")
                
            # Hashrate
            hashrate = stats.get('hashrate', 0)
            if hashrate > 1000000:
                hr_str = f"{hashrate/1000000:.2f} MH/s"
            elif hashrate > 1000:
                hr_str = f"{hashrate/1000:.2f} KH/s"
            else:
                hr_str = f"{hashrate:.2f} H/s"
            print(f"║  ⚡ Hashrate: {hr_str:<45} ║")
            
            # System
            cpu = stats.get('cpu_usage', 0)
            temp = stats.get('temperature', 0)
            threads = stats.get('active_threads', 0)
            print(f"║  🖥️  CPU: {cpu:.1f}% | Temp: {temp:.1f}°C | Threads: {threads:<17} ║")
            
            # Mining results
            accepted = stats.get('accepted_shares', 0)
            rejected = stats.get('rejected_shares', 0)
            eff = (accepted/(accepted+rejected))*100 if (accepted+rejected) > 0 else 0
            print(f"║  ✅ Accepted: {accepted} | ❌ Rejected: {rejected} | 📊 Efficiency: {eff:.1f}%{'':<8} ║")
            
            print("╠══════════════════════════════════════════════════════════╣")
            
            # Web monitor info
            web_port = self.config.get('web_port', 0)
            if web_port > 0:
                print(f"║  📊 Web Monitor: http://localhost:{web_port}{'':<25} ║")
            
            print("║  🛑 Press Ctrl+C to stop mining{'':<28} ║")
            print("╚══════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            logger.debug(f"Stats display error: {e}")
            
    def show_final_stats(self):
        """Show final statistics"""
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            print(f"\n📊 Final Statistics:")
            print(f"   Runtime: {str(runtime).split('.')[0]}")
            print(f"   Average Hashrate: {self.stats['last_hashrate']:.2f} H/s")
            print(f"   Total Hashes: {self.stats['total_hashes']:,}")
            
    def setup_web_monitor(self):
        """Setup optional web monitoring"""
        if not WEB_AVAILABLE or self.config.get('web_port', 0) <= 0:
            return
            
        self.web_app = FastAPI(title="CryptoMiner Pro V30")
        
        @self.web_app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self.get_web_dashboard()
            
        @self.web_app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.web_connections.append(websocket)
            
            try:
                while True:
                    if self.mining_engine:
                        status = self.mining_engine.get_mining_status()
                        await websocket.send_json({
                            "type": "stats",
                            "data": status,
                            "timestamp": datetime.now().isoformat()
                        })
                    await asyncio.sleep(2)
                    
            except WebSocketDisconnect:
                if websocket in self.web_connections:
                    self.web_connections.remove(websocket)
                    
    def get_web_dashboard(self):
        """Generate web dashboard HTML"""
        return f"""<!DOCTYPE html>
<html><head><title>CryptoMiner Pro V30</title>
<style>
body {{ font-family: Arial; background: linear-gradient(135deg, #1e3c72, #2a5298); 
       color: white; margin: 0; padding: 20px; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
.header {{ text-align: center; margin-bottom: 30px; padding: 20px; 
           background: rgba(255,255,255,0.1); border-radius: 15px; }}
.header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
          gap: 20px; }}
.stat-card {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; }}
.stat-value {{ font-size: 2rem; font-weight: bold; color: #4CAF50; }}
.status {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; 
           margin-right: 8px; background: #4CAF50; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0%{{opacity:1}} 50%{{opacity:0.5}} 100%{{opacity:1}} }}
</style></head>
<body>
<div class="container">
<div class="header">
<h1>🚀 CryptoMiner Pro V30</h1>
<div><span class="status"></span>Terminal Mining Monitor</div>
</div>
<div class="stats">
<div class="stat-card"><h3>⚡ Hashrate</h3><div class="stat-value" id="hashrate">0 H/s</div></div>
<div class="stat-card"><h3>🖥️ System</h3><div class="stat-value" id="cpu">0%</div><div id="temp">0°C</div></div>
<div class="stat-card"><h3>📊 Stats</h3><div>✅ <span id="accepted">0</span> | ❌ <span id="rejected">0</span></div></div>
<div class="stat-card"><h3>⏱️ Runtime</h3><div class="stat-value" id="runtime">00:00:00</div></div>
</div></div>
<script>
const ws = new WebSocket('ws://localhost:{self.config.get("web_port", 3333)}/ws');
let startTime = new Date();
ws.onmessage = function(event) {{
    const data = JSON.parse(event.data);
    if (data.type === 'stats') {{
        const stats = data.data.stats || {{}};
        const hashrate = stats.hashrate || 0;
        document.getElementById('hashrate').textContent = 
            hashrate > 1000000 ? (hashrate/1000000).toFixed(2) + ' MH/s' :
            hashrate > 1000 ? (hashrate/1000).toFixed(2) + ' KH/s' :
            hashrate.toFixed(2) + ' H/s';
        document.getElementById('cpu').textContent = (stats.cpu_usage || 0).toFixed(1) + '%';
        document.getElementById('temp').textContent = (stats.temperature || 0).toFixed(1) + '°C';
        document.getElementById('accepted').textContent = stats.accepted_shares || 0;
        document.getElementById('rejected').textContent = stats.rejected_shares || 0;
        
        const runtime = Math.floor((new Date() - startTime) / 1000);
        const hours = Math.floor(runtime / 3600);
        const minutes = Math.floor((runtime % 3600) / 60);
        const seconds = runtime % 60;
        document.getElementById('runtime').textContent = 
            hours.toString().padStart(2,'0') + ':' +
            minutes.toString().padStart(2,'0') + ':' +
            seconds.toString().padStart(2,'0');
    }}
}};
setInterval(() => {{
    const runtime = Math.floor((new Date() - startTime) / 1000);
    const hours = Math.floor(runtime / 3600);
    const minutes = Math.floor((runtime % 3600) / 60);
    const seconds = runtime % 60;
    document.getElementById('runtime').textContent = 
        hours.toString().padStart(2,'0') + ':' +
        minutes.toString().padStart(2,'0') + ':' +
        seconds.toString().padStart(2,'0');
}}, 1000);
</script></body></html>"""
        
    def start_web_monitor(self):
        """Start web monitoring server"""
        if not self.web_app or self.config.get('web_port', 0) <= 0:
            return
            
        def run_server():
            try:
                uvicorn.run(
                    self.web_app,
                    host="127.0.0.1",
                    port=self.config['web_port'],
                    log_level="error",
                    access_log=False
                )
            except Exception as e:
                logger.debug(f"Web server error: {e}")
                
        threading.Thread(target=run_server, daemon=True).start()
        time.sleep(1)  # Give server time to start
        
    def run(self):
        """Main mining loop"""
        while self.running:
            try:
                self.show_stats()
                time.sleep(3)  # Update every 3 seconds
            except KeyboardInterrupt:
                break
        self.stop_mining()

def main():
    parser = argparse.ArgumentParser(
        description='CryptoMiner Pro V30 - Compact Terminal Application'
    )
    parser.add_argument('--setup', action='store_true', help='Interactive setup')
    parser.add_argument('--config', help='Config file to use')  
    parser.add_argument('--coin', help='Coin symbol (LTC, DOGE, FTC)')
    parser.add_argument('--wallet', help='Wallet address')
    parser.add_argument('--pool', help='Pool address')
    parser.add_argument('--threads', type=int, help='Number of threads')
    parser.add_argument('--web-port', type=int, default=3333, help='Web monitor port (0 to disable)')
    parser.add_argument('--list-coins', action='store_true', help='List available coins')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    miner = CompactMiner()
    miner.setup_signal_handlers()
    miner.print_banner()
    
    if args.list_coins:
        print("📈 Available Coins:")
        for _, coin in get_coin_presets().items():
            print(f"  {coin['symbol']:<6} - {coin['name']}")
        return 0
        
    try:
        miner.initialize_components()
        
        # Load config
        if args.config:
            miner.load_config(args.config)
        else:
            miner.load_config()
            
        # Setup mode
        if args.setup:
            miner.interactive_setup()
            return 0
            
        # Command line config
        if args.coin and args.wallet:
            coin_presets = get_coin_presets()
            coin_data = None
            for coin in coin_presets.values():
                if coin['symbol'].upper() == args.coin.upper():
                    coin_data = coin
                    break
                    
            if not coin_data:
                print(f"❌ Unknown coin: {args.coin}")
                return 1
                
            is_valid, message = validate_wallet_address(args.wallet, coin_data['symbol'])
            if not is_valid:
                print(f"❌ {message}")
                return 1
                
            miner.config = {
                'coin': coin_data,
                'wallet_address': args.wallet,
                'mode': 'pool' if args.pool else 'solo',
                'threads': args.threads or coin_data.get('default_threads', 8),
                'web_port': args.web_port
            }
            
            if args.pool:
                miner.config['pool_address'] = args.pool
                
        # Check config
        if not miner.config:
            print("⚠️  No configuration found!")
            print("Options:")
            print("  python3 mine.py --setup           # Interactive setup")
            print("  python3 mine.py --list-coins      # Show available coins")
            print("  python3 mine.py --coin LTC --wallet ADDRESS --pool POOL")
            return 1
            
        # Setup web monitoring
        if WEB_AVAILABLE and miner.config.get('web_port', 0) > 0:
            try:
                miner.setup_web_monitor()
                miner.start_web_monitor()
                print(f"📊 Web monitor: http://localhost:{miner.config['web_port']}")
            except Exception as e:
                logger.warning(f"Web monitor failed: {e}")
                
        # Start mining
        if miner.start_mining():
            print("⛏️ Mining started... Press Ctrl+C to stop")
            miner.run()
        else:
            print("❌ Failed to start mining")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())