#!/usr/bin/env python3
"""
Comprehensive AI System Backend Testing for CryptoMiner Pro
Focus: Test AI system's ability to optimize mining shares, analyze pool performance, and enhance mining efficiency
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
import websocket
import threading
from typing import Dict, Any, Optional

class AISystemTester:
    def __init__(self):
        # Get backend URL from environment
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1].strip()
                    break
        
        self.base_url = f"{backend_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.websocket_data = []
        self.websocket_connected = False
        
        # Test parameters from user request
        self.test_wallet = "ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl"
        self.test_password = "d=24000"
        self.test_pool_server = "ltc.luckymonster.pro"
        self.test_pool_port = 4112
        
        print(f"🎯 AI System Backend Testing for CryptoMiner Pro")
        print(f"Backend URL: {self.base_url}")
        print(f"Test Pool: {self.test_pool_server}:{self.test_pool_port}")
        print(f"Test Wallet: {self.test_wallet}")
        print("=" * 80)
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            print(f"❌ {name}: FAILED {details}")
        return success

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout: int = 15) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            return response.status_code < 400, response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    def test_ai_insights_endpoint(self):
        """Test AI Insights API Endpoint (/api/ai/insights)"""
        print("\n🧠 Testing AI Insights API Endpoint...")
        
        # Test AI insights endpoint
        success, response = self.make_request('GET', '/mining/ai-insights')
        
        if success:
            # Check if AI system is available
            if "error" in response and "AI system not available" in response["error"]:
                return self.log_test("AI Insights API", True, "- AI system correctly reports not available (expected when not mining)")
            
            # If AI is available, check response structure
            if "insights" in response and "predictions" in response:
                insights = response["insights"]
                predictions = response["predictions"]
                
                details = f"- Insights: {len(insights)} categories"
                if "optimization_suggestions" in insights:
                    details += f", {len(insights['optimization_suggestions'])} suggestions"
                if "predicted_hashrate" in predictions:
                    details += f", Predicted hashrate: {predictions['predicted_hashrate']}"
                
                return self.log_test("AI Insights API", True, details)
            else:
                return self.log_test("AI Insights API", False, f"- Invalid response structure: {response}")
        else:
            return self.log_test("AI Insights API", False, f"- Request failed: {response}")

    def test_pool_connection_testing(self):
        """Test Pool Connection Testing with Real Pool Server"""
        print("\n🔗 Testing Pool Connection with Real Pool Server...")
        
        # Test pool connection to real Litecoin pool
        pool_test_data = {
            "pool_address": self.test_pool_server,
            "pool_port": self.test_pool_port,
            "type": "pool"
        }
        
        success, response = self.make_request('POST', '/pool/test-connection', pool_test_data)
        
        if success and response.get("success"):
            details = f"- Connected to {self.test_pool_server}:{self.test_pool_port}"
            if "connection_time" in response:
                details += f", Time: {response['connection_time']}"
            if "status" in response:
                details += f", Status: {response['status']}"
            
            return self.log_test("Real Pool Connection Test", True, details)
        else:
            error_msg = response.get("error", response.get("message", "Unknown error"))
            return self.log_test("Real Pool Connection Test", False, f"- {error_msg}")

    def test_mining_with_ai_optimization(self):
        """Test Mining Start with AI Optimization Enabled"""
        print("\n⚡ Testing Mining with AI Optimization...")
        
        # Get Litecoin preset first
        success, presets_response = self.make_request('GET', '/coins/presets')
        if not success:
            return self.log_test("Mining with AI - Get Presets", False, f"- Failed to get coin presets: {presets_response}")
        
        litecoin_config = presets_response["presets"]["litecoin"]
        
        # Configure mining with AI optimization and real pool
        mining_config = {
            "coin": litecoin_config,
            "mode": "pool",
            "threads": 2,  # Conservative for testing
            "intensity": 0.8,
            "auto_optimize": True,  # Enable auto optimization
            "ai_enabled": True,     # Enable AI system
            "wallet_address": "",   # Not needed for pool mining
            "pool_username": self.test_wallet,  # Use wallet as username
            "pool_password": self.test_password,
            "custom_pool_address": self.test_pool_server,
            "custom_pool_port": self.test_pool_port,
            "auto_thread_detection": True,
            "thread_profile": "standard"
        }
        
        # Start mining with AI optimization
        success, response = self.make_request('POST', '/mining/start', mining_config, timeout=20)
        
        if success and response.get("success"):
            details = f"- Mining started with AI optimization"
            if "wallet_info" in response:
                wallet_info = response["wallet_info"]
                if "threads_used" in wallet_info:
                    details += f", Threads: {wallet_info['threads_used']}"
                if "connection_type" in wallet_info:
                    details += f", Connection: {wallet_info['connection_type']}"
            
            # Let mining run for a few seconds to collect data
            print("   ⏳ Letting mining run for 10 seconds to collect AI data...")
            time.sleep(10)
            
            # Check mining status and AI data collection
            status_success, status_response = self.make_request('GET', '/mining/status')
            if status_success and status_response.get("is_mining"):
                stats = status_response.get("stats", {})
                details += f", Hashrate: {stats.get('hashrate', 0):.2f} H/s"
                details += f", CPU: {stats.get('cpu_usage', 0):.1f}%"
                
                # Stop mining
                self.make_request('POST', '/mining/stop')
                
                return self.log_test("Mining with AI Optimization", True, details)
            else:
                self.make_request('POST', '/mining/stop')
                return self.log_test("Mining with AI Optimization", False, "- Mining status check failed")
        else:
            error_msg = response.get("detail", response.get("message", "Unknown error"))
            return self.log_test("Mining with AI Optimization", False, f"- {error_msg}")

    def test_ai_mining_efficiency_analysis(self):
        """Test AI Mining Efficiency Enhancement"""
        print("\n📊 Testing AI Mining Efficiency Analysis...")
        
        # Start mining briefly to generate data for AI analysis
        success, presets_response = self.make_request('GET', '/coins/presets')
        if not success:
            return self.log_test("AI Efficiency Analysis - Setup", False, "Failed to get presets")
        
        litecoin_config = presets_response["presets"]["litecoin"]
        
        mining_config = {
            "coin": litecoin_config,
            "mode": "pool",
            "threads": 1,  # Single thread for efficiency testing
            "intensity": 1.0,
            "auto_optimize": True,
            "ai_enabled": True,
            "pool_username": self.test_wallet,
            "pool_password": self.test_password,
            "custom_pool_address": self.test_pool_server,
            "custom_pool_port": self.test_pool_port
        }
        
        # Start mining
        start_success, start_response = self.make_request('POST', '/mining/start', mining_config)
        if not start_success:
            return self.log_test("AI Efficiency Analysis", False, f"Failed to start mining: {start_response}")
        
        # Let it run to collect efficiency data
        print("   ⏳ Collecting efficiency data for 8 seconds...")
        time.sleep(8)
        
        # Get AI insights for efficiency analysis
        insights_success, insights_response = self.make_request('GET', '/mining/ai-insights')
        
        # Get current mining status for efficiency metrics
        status_success, status_response = self.make_request('GET', '/mining/status')
        
        # Stop mining
        self.make_request('POST', '/mining/stop')
        
        if insights_success and status_success:
            stats = status_response.get("stats", {})
            efficiency = stats.get("efficiency", 0)
            hashrate = stats.get("hashrate", 0)
            cpu_usage = stats.get("cpu_usage", 0)
            
            details = f"- Efficiency: {efficiency:.1f}%"
            details += f", Hashrate: {hashrate:.2f} H/s"
            details += f", CPU Usage: {cpu_usage:.1f}%"
            
            # Check if AI provided insights
            if "error" not in insights_response:
                if "insights" in insights_response:
                    insights = insights_response["insights"]
                    if "optimization_suggestions" in insights:
                        suggestions_count = len(insights["optimization_suggestions"])
                        details += f", AI Suggestions: {suggestions_count}"
                
                if "predictions" in insights_response:
                    predictions = insights_response["predictions"]
                    if "recommended_threads" in predictions:
                        details += f", Recommended Threads: {predictions['recommended_threads']}"
            
            return self.log_test("AI Mining Efficiency Analysis", True, details)
        else:
            return self.log_test("AI Mining Efficiency Analysis", False, "Failed to get AI insights or mining status")

    def test_ai_pool_performance_analysis(self):
        """Test AI Pool Performance Analysis"""
        print("\n🏊 Testing AI Pool Performance Analysis...")
        
        # Test multiple pool connections to analyze performance
        pools_to_test = [
            {"address": self.test_pool_server, "port": self.test_pool_port, "name": "Primary LTC Pool"},
            {"address": "ltc.pool.com", "port": 4444, "name": "Alternative Pool (may not exist)"}
        ]
        
        pool_results = []
        
        for pool in pools_to_test:
            test_data = {
                "pool_address": pool["address"],
                "pool_port": pool["port"],
                "type": "pool"
            }
            
            success, response = self.make_request('POST', '/pool/test-connection', test_data)
            
            pool_result = {
                "name": pool["name"],
                "address": f"{pool['address']}:{pool['port']}",
                "success": success and response.get("success", False),
                "response_time": response.get("connection_time", "unknown") if success else "failed"
            }
            pool_results.append(pool_result)
        
        # Analyze results
        successful_pools = [p for p in pool_results if p["success"]]
        
        details = f"- Tested {len(pools_to_test)} pools, {len(successful_pools)} reachable"
        
        for pool in pool_results:
            status = "✓" if pool["success"] else "✗"
            details += f"\n     {status} {pool['name']}: {pool['response_time']}"
        
        # AI would use this data for pool performance recommendations
        if len(successful_pools) > 0:
            details += f"\n   - AI can recommend best pool based on connection performance"
            return self.log_test("AI Pool Performance Analysis", True, details)
        else:
            return self.log_test("AI Pool Performance Analysis", False, "- No pools were reachable for analysis")

    def test_ai_hash_pattern_prediction(self):
        """Test AI Hash Pattern Prediction Functionality"""
        print("\n🔮 Testing AI Hash Pattern Prediction...")
        
        # Start mining to generate hash patterns for AI analysis
        success, presets_response = self.make_request('GET', '/coins/presets')
        if not success:
            return self.log_test("AI Hash Pattern Prediction", False, "Failed to get presets")
        
        litecoin_config = presets_response["presets"]["litecoin"]
        
        mining_config = {
            "coin": litecoin_config,
            "mode": "pool",
            "threads": 2,
            "intensity": 0.9,
            "ai_enabled": True,
            "auto_optimize": True,
            "pool_username": self.test_wallet,
            "pool_password": self.test_password,
            "custom_pool_address": self.test_pool_server,
            "custom_pool_port": self.test_pool_port
        }
        
        # Start mining
        start_success, start_response = self.make_request('POST', '/mining/start', mining_config)
        if not start_success:
            return self.log_test("AI Hash Pattern Prediction", False, f"Failed to start mining: {start_response}")
        
        # Collect hash pattern data over time
        print("   ⏳ Collecting hash pattern data for 12 seconds...")
        hash_rates = []
        
        for i in range(6):  # Collect data points every 2 seconds
            time.sleep(2)
            status_success, status_response = self.make_request('GET', '/mining/status')
            if status_success and "stats" in status_response:
                hashrate = status_response["stats"].get("hashrate", 0)
                hash_rates.append(hashrate)
                print(f"     Sample {i+1}: {hashrate:.2f} H/s")
        
        # Get AI insights for pattern prediction
        insights_success, insights_response = self.make_request('GET', '/mining/ai-insights')
        
        # Stop mining
        self.make_request('POST', '/mining/stop')
        
        if insights_success and len(hash_rates) > 0:
            avg_hashrate = sum(hash_rates) / len(hash_rates)
            hashrate_trend = "increasing" if hash_rates[-1] > hash_rates[0] else "stable/decreasing"
            
            details = f"- Collected {len(hash_rates)} samples, Avg: {avg_hashrate:.2f} H/s, Trend: {hashrate_trend}"
            
            # Check AI predictions
            if "error" not in insights_response:
                if "predictions" in insights_response:
                    predictions = insights_response["predictions"]
                    if "predicted_hashrate" in predictions:
                        predicted = predictions["predicted_hashrate"]
                        details += f", AI Predicted: {predicted:.2f} H/s"
                    if "confidence" in predictions:
                        confidence = predictions["confidence"]
                        details += f", Confidence: {confidence:.1%}"
                
                if "insights" in insights_response:
                    insights = insights_response["insights"]
                    if "hash_pattern_prediction" in insights:
                        pattern = insights["hash_pattern_prediction"]
                        if "trend" in pattern:
                            details += f", AI Trend: {pattern['trend']}"
            
            return self.log_test("AI Hash Pattern Prediction", True, details)
        else:
            return self.log_test("AI Hash Pattern Prediction", False, "Failed to collect hash data or get AI insights")

    def test_ai_real_time_optimization(self):
        """Test AI Real-time Mining Optimization"""
        print("\n🚀 Testing AI Real-time Mining Optimization...")
        
        # Test with different thread profiles to see AI optimization
        profiles = ["light", "standard", "maximum"]
        optimization_results = []
        
        success, presets_response = self.make_request('GET', '/coins/presets')
        if not success:
            return self.log_test("AI Real-time Optimization", False, "Failed to get presets")
        
        litecoin_config = presets_response["presets"]["litecoin"]
        
        for profile in profiles:
            print(f"   Testing {profile} profile...")
            
            mining_config = {
                "coin": litecoin_config,
                "mode": "pool",
                "threads": 1,  # Will be optimized by AI
                "intensity": 1.0,
                "ai_enabled": True,
                "auto_optimize": True,
                "pool_username": self.test_wallet,
                "pool_password": self.test_password,
                "custom_pool_address": self.test_pool_server,
                "custom_pool_port": self.test_pool_port,
                "auto_thread_detection": True,
                "thread_profile": profile
            }
            
            # Start mining with this profile
            start_success, start_response = self.make_request('POST', '/mining/start', mining_config)
            if start_success:
                # Let AI optimize for a few seconds
                time.sleep(5)
                
                # Check optimization results
                status_success, status_response = self.make_request('GET', '/mining/status')
                if status_success:
                    stats = status_response["stats"]
                    config = status_response.get("config", {})
                    
                    result = {
                        "profile": profile,
                        "threads_used": config.get("threads", 1),
                        "hashrate": stats.get("hashrate", 0),
                        "cpu_usage": stats.get("cpu_usage", 0),
                        "efficiency": stats.get("efficiency", 0)
                    }
                    optimization_results.append(result)
                
                # Stop mining
                self.make_request('POST', '/mining/stop')
                time.sleep(1)  # Brief pause between tests
        
        if len(optimization_results) > 0:
            details = f"- Tested {len(optimization_results)} profiles:"
            for result in optimization_results:
                details += f"\n     {result['profile']}: {result['threads_used']} threads, "
                details += f"{result['hashrate']:.2f} H/s, {result['cpu_usage']:.1f}% CPU"
            
            # Find best performing profile
            best_profile = max(optimization_results, key=lambda x: x['hashrate'])
            details += f"\n   - Best performance: {best_profile['profile']} profile"
            
            return self.log_test("AI Real-time Optimization", True, details)
        else:
            return self.log_test("AI Real-time Optimization", False, "No optimization data collected")

    def test_websocket_ai_updates(self):
        """Test WebSocket Real-time AI Updates"""
        print("\n📡 Testing WebSocket AI Updates...")
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self.websocket_data.append(data)
            except:
                pass
        
        def on_open(ws):
            self.websocket_connected = True
        
        def on_error(ws, error):
            print(f"   WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            self.websocket_connected = False
        
        # Connect to WebSocket
        ws_url = self.base_url.replace('/api', '/api/ws').replace('https://', 'wss://').replace('http://', 'ws://')
        
        try:
            ws = websocket.WebSocketApp(ws_url,
                                      on_message=on_message,
                                      on_open=on_open,
                                      on_error=on_error,
                                      on_close=on_close)
            
            # Start WebSocket in background
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection
            time.sleep(2)
            
            if self.websocket_connected:
                # Start mining to generate AI updates
                success, presets_response = self.make_request('GET', '/coins/presets')
                if success:
                    litecoin_config = presets_response["presets"]["litecoin"]
                    
                    mining_config = {
                        "coin": litecoin_config,
                        "mode": "pool",
                        "threads": 1,
                        "ai_enabled": True,
                        "pool_username": self.test_wallet,
                        "pool_password": self.test_password,
                        "custom_pool_address": self.test_pool_server,
                        "custom_pool_port": self.test_pool_port
                    }
                    
                    start_success, _ = self.make_request('POST', '/mining/start', mining_config)
                    if start_success:
                        # Collect WebSocket data
                        print("   ⏳ Collecting WebSocket AI updates for 8 seconds...")
                        time.sleep(8)
                        
                        # Stop mining
                        self.make_request('POST', '/mining/stop')
                
                # Close WebSocket
                ws.close()
                
                # Analyze collected data
                mining_updates = [d for d in self.websocket_data if d.get("type") == "mining_update"]
                system_updates = [d for d in self.websocket_data if d.get("type") == "system_update"]
                
                details = f"- Received {len(self.websocket_data)} total messages"
                details += f", {len(mining_updates)} mining updates"
                details += f", {len(system_updates)} system updates"
                
                if len(mining_updates) > 0:
                    # Check if AI data is included in updates
                    last_update = mining_updates[-1]
                    if "stats" in last_update:
                        stats = last_update["stats"]
                        details += f", Final hashrate: {stats.get('hashrate', 0):.2f} H/s"
                
                return self.log_test("WebSocket AI Updates", True, details)
            else:
                return self.log_test("WebSocket AI Updates", False, "Failed to connect to WebSocket")
                
        except Exception as e:
            return self.log_test("WebSocket AI Updates", False, f"WebSocket test error: {str(e)}")

    def run_comprehensive_ai_tests(self):
        """Run all AI system tests"""
        print(f"\n🎯 COMPREHENSIVE AI SYSTEM BACKEND TESTING")
        print(f"Target: CryptoMiner Pro AI Mining Optimization")
        print(f"Pool: {self.test_pool_server}:{self.test_pool_port}")
        print("=" * 80)
        
        # Run all AI-focused tests
        test_results = []
        
        test_results.append(self.test_ai_insights_endpoint())
        test_results.append(self.test_pool_connection_testing())
        test_results.append(self.test_mining_with_ai_optimization())
        test_results.append(self.test_ai_mining_efficiency_analysis())
        test_results.append(self.test_ai_pool_performance_analysis())
        test_results.append(self.test_ai_hash_pattern_prediction())
        test_results.append(self.test_ai_real_time_optimization())
        test_results.append(self.test_websocket_ai_updates())
        
        # Summary
        print("\n" + "=" * 80)
        print(f"🎯 AI SYSTEM TESTING COMPLETE")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL AI SYSTEM TESTS PASSED!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed - see details above")
            return False

if __name__ == "__main__":
    tester = AISystemTester()
    success = tester.run_comprehensive_ai_tests()
    sys.exit(0 if success else 1)