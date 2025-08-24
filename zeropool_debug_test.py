#!/usr/bin/env python3
"""
CryptoMiner V21 - Zeropool.io Connection Proxy Debug Test
Enhanced debugging test to analyze zeropool.io login response and job acquisition
"""

import requests
import json
import time
import sys
import subprocess
import threading
import logging
from datetime import datetime
from typing import Dict, Any, List

# Use the production backend URL from frontend/.env
BACKEND_URL = "https://smartcrypto-5.preview.emergentagent.com/api"

class ZeropoolDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.mining_process = None
        self.log_monitor_thread = None
        self.monitoring_active = False
        self.debug_logs = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def start_log_monitoring(self):
        """Start monitoring mining process logs for specific debug messages"""
        self.monitoring_active = True
        self.log_monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        self.log_monitor_thread.start()
        print("🔍 Started log monitoring for zeropool.io debug messages")
    
    def stop_log_monitoring(self):
        """Stop log monitoring"""
        self.monitoring_active = False
        if self.log_monitor_thread:
            self.log_monitor_thread.join(timeout=2)
        print("🛑 Stopped log monitoring")
    
    def _monitor_logs(self):
        """Monitor mining process logs for specific debug patterns"""
        debug_patterns = [
            "LOGIN RESPONSE ANALYSIS",
            "JOB_LISTENER RECV", 
            "NEW JOB NOTIFICATION",
            "local_",  # Local job IDs
            "📤 SEND",
            "📥 RECV",
            "job_id",
            "zeropool.io",
            "authentication",
            "share submission"
        ]
        
        while self.monitoring_active:
            try:
                if self.mining_process and self.mining_process.poll() is None:
                    # Read stdout
                    if self.mining_process.stdout:
                        line = self.mining_process.stdout.readline()
                        if line:
                            log_line = line.strip()
                            self.debug_logs.append({
                                'timestamp': datetime.now().isoformat(),
                                'source': 'stdout',
                                'message': log_line
                            })
                            
                            # Check for specific patterns
                            for pattern in debug_patterns:
                                if pattern in log_line:
                                    print(f"🔍 DEBUG FOUND: {pattern} -> {log_line}")
                    
                    # Read stderr
                    if self.mining_process.stderr:
                        line = self.mining_process.stderr.readline()
                        if line:
                            log_line = line.strip()
                            self.debug_logs.append({
                                'timestamp': datetime.now().isoformat(),
                                'source': 'stderr', 
                                'message': log_line
                            })
                            
                            # Check for specific patterns
                            for pattern in debug_patterns:
                                if pattern in log_line:
                                    print(f"🔍 DEBUG FOUND: {pattern} -> {log_line}")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                print(f"❌ Log monitoring error: {e}")
                time.sleep(1)
    
    def test_api_health(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "CryptoMiner V21 API" in data.get("message", ""):
                    self.log_test("API Health Check", True, "Backend API is accessible and responding")
                    return True
                else:
                    self.log_test("API Health Check", False, f"Unexpected API response: {data}")
                    return False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_start_xmr_mining_zeropool(self):
        """Start XMR mining specifically with zeropool.io to trigger authentication"""
        try:
            # Stop any existing mining first
            self._stop_existing_mining()
            
            # Configuration specifically for zeropool.io debugging
            mining_config = {
                "action": "start",
                "config": {
                    "coin": "XMR",
                    "wallet": "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                    "pool": "stratum+tcp://xmr.zeropool.io:3333",
                    "intensity": 80,
                    "threads": 4,
                    "password": "x"
                }
            }
            
            print("🚀 Starting XMR mining with zeropool.io for debug analysis...")
            response = self.session.post(f"{BACKEND_URL}/mining/control", json=mining_config)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Start XMR Mining (Zeropool)", True, 
                                f"Mining started successfully with PID: {data.get('process_id', 'N/A')}", data)
                    return True
                else:
                    self.log_test("Start XMR Mining (Zeropool)", False, 
                                f"Start failed: {data.get('message', 'Unknown error')}", data)
                    return False
            else:
                self.log_test("Start XMR Mining (Zeropool)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Start XMR Mining (Zeropool)", False, f"Error: {str(e)}")
            return False
    
    def test_login_response_analysis(self):
        """Monitor for LOGIN RESPONSE ANALYSIS messages during authentication"""
        print("🔍 Monitoring for LOGIN RESPONSE ANALYSIS messages...")
        
        # Wait for authentication to complete
        time.sleep(10)
        
        # Check debug logs for login response analysis
        login_analysis_found = False
        job_data_found = False
        
        for log_entry in self.debug_logs:
            message = log_entry['message']
            if "LOGIN RESPONSE ANALYSIS" in message:
                login_analysis_found = True
                print(f"✅ Found LOGIN RESPONSE ANALYSIS: {message}")
                
                # Check if job data was provided
                if "JOB DATA RECEIVED" in message or "job_id" in message.lower():
                    job_data_found = True
                    print(f"📋 Job data detected in login response")
        
        if login_analysis_found:
            self.log_test("Login Response Analysis", True, 
                        f"LOGIN RESPONSE ANALYSIS messages found, Job data: {'Yes' if job_data_found else 'No'}")
            return True
        else:
            self.log_test("Login Response Analysis", False, 
                        "No LOGIN RESPONSE ANALYSIS messages found in logs")
            return False
    
    def test_job_listener_verification(self):
        """Verify job listener worker starts and monitors for job notifications"""
        print("👂 Verifying job listener worker and monitoring for job notifications...")
        
        # Wait for job listener to start
        time.sleep(5)
        
        job_listener_started = False
        job_recv_messages = False
        new_job_notifications = False
        
        for log_entry in self.debug_logs:
            message = log_entry['message']
            
            if "job listener" in message.lower() or "JOB_LISTENER" in message:
                job_listener_started = True
                print(f"✅ Job listener activity: {message}")
            
            if "JOB_LISTENER RECV" in message:
                job_recv_messages = True
                print(f"📥 Job listener received message: {message}")
            
            if "NEW JOB NOTIFICATION" in message:
                new_job_notifications = True
                print(f"🔔 New job notification: {message}")
        
        success = job_listener_started
        details = {
            'job_listener_started': job_listener_started,
            'job_recv_messages': job_recv_messages,
            'new_job_notifications': new_job_notifications
        }
        
        self.log_test("Job Listener Verification", success, 
                    f"Job listener active: {job_listener_started}, RECV messages: {job_recv_messages}, Notifications: {new_job_notifications}",
                    details)
        return success
    
    def test_real_vs_local_jobs(self):
        """Monitor share submissions to identify real vs local job IDs"""
        print("🎯 Analyzing share submissions for real vs local job IDs...")
        
        # Wait for mining to generate some shares
        time.sleep(20)
        
        local_job_ids = []
        real_job_ids = []
        share_submissions = []
        
        for log_entry in self.debug_logs:
            message = log_entry['message']
            
            # Look for share submissions
            if "share" in message.lower() and ("submit" in message.lower() or "job" in message.lower()):
                share_submissions.append(message)
                
                # Check for local job IDs
                if "local_" in message:
                    local_job_ids.append(message)
                    print(f"🏠 Local job ID found: {message}")
                
                # Check for real pool job IDs (not starting with local_)
                if "job_id" in message.lower() and "local_" not in message:
                    real_job_ids.append(message)
                    print(f"🌐 Real pool job ID found: {message}")
        
        total_shares = len(share_submissions)
        local_count = len(local_job_ids)
        real_count = len(real_job_ids)
        
        details = {
            'total_share_submissions': total_shares,
            'local_job_count': local_count,
            'real_job_count': real_count,
            'local_job_samples': local_job_ids[:3],  # First 3 samples
            'real_job_samples': real_job_ids[:3]     # First 3 samples
        }
        
        # Success if we found any share activity
        success = total_shares > 0
        message = f"Share analysis: {total_shares} total, {local_count} local jobs, {real_count} real jobs"
        
        self.log_test("Real vs Local Jobs Analysis", success, message, details)
        return success
    
    def test_protocol_message_flow(self):
        """Analyze complete SEND/RECV message flow during login"""
        print("📡 Analyzing protocol message flow (SEND/RECV) during authentication...")
        
        send_messages = []
        recv_messages = []
        
        for log_entry in self.debug_logs:
            message = log_entry['message']
            
            if "📤 SEND" in message or "SEND:" in message:
                send_messages.append(message)
                print(f"📤 SEND: {message}")
            
            if "📥 RECV" in message or "RECV:" in message:
                recv_messages.append(message)
                print(f"📥 RECV: {message}")
        
        send_count = len(send_messages)
        recv_count = len(recv_messages)
        
        details = {
            'send_message_count': send_count,
            'recv_message_count': recv_count,
            'send_samples': send_messages[:5],  # First 5 samples
            'recv_samples': recv_messages[:5]   # First 5 samples
        }
        
        # Success if we found protocol communication
        success = send_count > 0 and recv_count > 0
        message = f"Protocol flow: {send_count} SEND messages, {recv_count} RECV messages"
        
        self.log_test("Protocol Message Flow", success, message, details)
        return success
    
    def test_connection_diagnostics(self):
        """Verify connection stability with job listener"""
        print("🔗 Testing connection stability and diagnostics...")
        
        try:
            # Check mining status
            response = self.session.get(f"{BACKEND_URL}/mining/status")
            if response.status_code == 200:
                status_data = response.json()
                is_active = status_data.get('is_active', False)
                pool_connected = status_data.get('pool_connected', False)
                
                # Check mining stats
                stats_response = self.session.get(f"{BACKEND_URL}/mining/stats")
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    hashrate = stats_data.get('hashrate', 0)
                    
                    # Connection is stable if mining is active and has hashrate
                    connection_stable = is_active and hashrate > 0
                    
                    details = {
                        'is_active': is_active,
                        'pool_connected': pool_connected,
                        'hashrate': hashrate,
                        'connection_stable': connection_stable
                    }
                    
                    message = f"Connection stable: {connection_stable}, Active: {is_active}, Pool: {pool_connected}, Hashrate: {hashrate}"
                    self.log_test("Connection Diagnostics", connection_stable, message, details)
                    return connection_stable
                else:
                    self.log_test("Connection Diagnostics", False, "Failed to get mining stats")
                    return False
            else:
                self.log_test("Connection Diagnostics", False, "Failed to get mining status")
                return False
        except Exception as e:
            self.log_test("Connection Diagnostics", False, f"Error: {str(e)}")
            return False
    
    def _stop_existing_mining(self):
        """Stop any existing mining processes"""
        try:
            stop_config = {"action": "stop"}
            response = self.session.post(f"{BACKEND_URL}/mining/control", json=stop_config)
            if response.status_code == 200:
                print("🛑 Stopped existing mining processes")
                time.sleep(3)  # Wait for processes to stop
        except Exception as e:
            print(f"⚠️ Error stopping existing mining: {e}")
    
    def run_zeropool_debug_test(self):
        """Run comprehensive zeropool.io debug test for 60+ seconds"""
        print("🚀 Starting CryptoMiner V21 Zeropool.io Connection Proxy Debug Test")
        print(f"🔗 Testing against: {BACKEND_URL}")
        print("🎯 Focus: Enhanced connection proxy debugging for zeropool.io login and job acquisition")
        print("=" * 80)
        
        # Start log monitoring
        self.start_log_monitoring()
        
        # Test sequence
        tests = [
            ("API Health Check", self.test_api_health),
            ("Start XMR Mining (Zeropool)", self.test_start_xmr_mining_zeropool),
            ("Login Response Analysis", self.test_login_response_analysis),
            ("Job Listener Verification", self.test_job_listener_verification),
            ("Real vs Local Jobs Analysis", self.test_real_vs_local_jobs),
            ("Protocol Message Flow", self.test_protocol_message_flow),
            ("Connection Diagnostics", self.test_connection_diagnostics)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔍 Running: {test_name}")
                if test_func():
                    passed += 1
                
                # Wait between tests for proper monitoring
                if test_name == "Start XMR Mining (Zeropool)":
                    print("⏳ Waiting 60+ seconds for complete authentication and job flow...")
                    time.sleep(65)  # Wait 65 seconds for complete flow analysis
                else:
                    time.sleep(5)
                    
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {str(e)}")
        
        # Stop log monitoring
        self.stop_log_monitoring()
        
        # Stop mining
        self._stop_existing_mining()
        
        print("=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        # Analyze findings
        self._analyze_debug_findings()
        
        return passed, total, self.test_results
    
    def _analyze_debug_findings(self):
        """Analyze debug findings to understand why real mining jobs aren't being received"""
        print("\n🔍 ZEROPOOL.IO DEBUG ANALYSIS:")
        print("=" * 50)
        
        # Count different types of messages
        login_analysis_count = 0
        job_listener_count = 0
        local_job_count = 0
        real_job_count = 0
        send_recv_count = 0
        auth_issues = 0
        
        for log_entry in self.debug_logs:
            message = log_entry['message']
            
            if "LOGIN RESPONSE ANALYSIS" in message:
                login_analysis_count += 1
            if "JOB_LISTENER" in message or "job listener" in message.lower():
                job_listener_count += 1
            if "local_" in message and "job" in message.lower():
                local_job_count += 1
            if "job_id" in message.lower() and "local_" not in message:
                real_job_count += 1
            if "📤 SEND" in message or "📥 RECV" in message:
                send_recv_count += 1
            if "unauthenticated" in message.lower() or "auth" in message.lower():
                auth_issues += 1
        
        print(f"📋 LOGIN RESPONSE ANALYSIS messages: {login_analysis_count}")
        print(f"👂 JOB LISTENER activity: {job_listener_count}")
        print(f"🏠 Local job IDs detected: {local_job_count}")
        print(f"🌐 Real pool job IDs detected: {real_job_count}")
        print(f"📡 SEND/RECV protocol messages: {send_recv_count}")
        print(f"🔐 Authentication issues: {auth_issues}")
        
        # Provide analysis
        print(f"\n💡 ANALYSIS:")
        if real_job_count == 0 and local_job_count > 0:
            print("❌ ISSUE: Only local job IDs found - zeropool.io not providing real mining jobs")
        elif real_job_count > 0:
            print("✅ SUCCESS: Real pool job IDs detected from zeropool.io")
        
        if login_analysis_count == 0:
            print("⚠️ WARNING: No LOGIN RESPONSE ANALYSIS messages - debug logging may not be active")
        
        if job_listener_count == 0:
            print("❌ ISSUE: No job listener activity detected")
        
        if auth_issues > 0:
            print(f"🔐 AUTHENTICATION: {auth_issues} authentication-related issues detected")
        
        print(f"\n📄 Total debug log entries captured: {len(self.debug_logs)}")

def main():
    """Main test execution"""
    tester = ZeropoolDebugTester()
    passed, total, results = tester.run_zeropool_debug_test()
    
    # Save detailed results
    with open('/app/zeropool_debug_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': (passed/total)*100,
                'timestamp': datetime.now().isoformat(),
                'test_duration': '60+ seconds',
                'focus': 'zeropool.io connection proxy debugging'
            },
            'detailed_results': results,
            'debug_logs': tester.debug_logs[-100:]  # Last 100 log entries
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/zeropool_debug_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed >= total * 0.6 else 1)  # 60% pass rate acceptable for debug test

if __name__ == "__main__":
    main()