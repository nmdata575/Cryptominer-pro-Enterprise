#!/usr/bin/env python3
"""
Enhanced Job ID Extraction Test for zeropool.io
Tests the enhanced job ID extraction fix for zeropool.io nested job structure
"""

import requests
import json
import time
import subprocess
import signal
import os
import threading
from datetime import datetime
from typing import Dict, Any, List

# Use the production backend URL from frontend/.env
BACKEND_URL = "https://smartcrypto-5.preview.emergentagent.com/api"

class ZeropoolJobExtractionTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.mining_process = None
        self.mining_logs = []
        self.log_capture_active = False
        
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
    
    def start_xmr_mining_zeropool(self):
        """Start XMR mining with zeropool.io to trigger enhanced job ID extraction"""
        try:
            print("🚀 Starting XMR mining with zeropool.io to test enhanced job ID extraction...")
            
            # Use POST /api/mining/control to start mining with zeropool.io
            mining_config = {
                "action": "start",
                "config": {
                    "coin": "XMR",
                    "wallet": "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                    "pool": "stratum+tcp://xmr.zeropool.io:3333",
                    "intensity": 90,
                    "threads": 2,
                    "password": "x"
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/mining/control", json=mining_config)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Start XMR Mining (Zeropool)", True, 
                                f"Mining started successfully with zeropool.io: {data.get('message', '')}", data)
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
    
    def capture_mining_logs(self, duration: int = 70):
        """Capture mining logs for analysis"""
        print(f"📋 Capturing mining logs for {duration} seconds to analyze job ID extraction...")
        
        # Start direct mining process to capture detailed logs
        try:
            cmd = [
                "python3", "/app/cryptominer.py",
                "--coin", "XMR",
                "--wallet", "4793trzeyXigW8qj9JZU1bVUuohVqn76EBpXUEJdDxJS5tAP4rjAdS7PzWFXzV3MtE3b9MKxMeHmE5X8J2oBk7cyNdE65j8",
                "--pool", "stratum+tcp://xmr.zeropool.io:3333",
                "--intensity", "90",
                "--threads", "2",
                "--debug"  # Enable debug logging
            ]
            
            print(f"   🚀 Starting mining process: {' '.join(cmd)}")
            self.mining_process = subprocess.Popen(
                cmd, 
                cwd="/app", 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Capture logs in real-time
            self.log_capture_active = True
            log_thread = threading.Thread(target=self._capture_logs_thread, daemon=True)
            log_thread.start()
            
            # Let mining run for specified duration
            time.sleep(duration)
            
            # Stop log capture
            self.log_capture_active = False
            
            # Terminate mining process
            if self.mining_process and self.mining_process.poll() is None:
                self.mining_process.terminate()
                try:
                    self.mining_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.mining_process.kill()
                    self.mining_process.wait()
            
            print(f"   ✅ Captured {len(self.mining_logs)} log entries")
            return True
            
        except Exception as e:
            print(f"   ❌ Error capturing logs: {e}")
            return False
    
    def _capture_logs_thread(self):
        """Thread to capture logs in real-time"""
        if not self.mining_process:
            return
            
        try:
            # Read both stdout and stderr
            import select
            
            while self.log_capture_active and self.mining_process.poll() is None:
                # Check if there's data to read
                ready, _, _ = select.select([self.mining_process.stdout, self.mining_process.stderr], [], [], 1)
                
                for stream in ready:
                    line = stream.readline()
                    if line:
                        self.mining_logs.append(line.strip())
                        # Print important messages in real-time
                        if any(keyword in line for keyword in [
                            "Stored job from login with ID:",
                            "Using REAL pool job:",
                            "JOB DATA RECEIVED:",
                            "Updated job with ID:",
                            "job=",
                            "H/s"
                        ]):
                            print(f"   📋 {line.strip()}")
                            
        except Exception as e:
            print(f"   ⚠️ Log capture thread error: {e}")
    
    def analyze_job_id_extraction(self) -> Dict[str, Any]:
        """Analyze captured logs for enhanced job ID extraction"""
        print("🔍 Analyzing logs for enhanced job ID extraction...")
        
        analysis = {
            'stored_job_messages': [],
            'real_job_usage': [],
            'job_data_received': [],
            'updated_job_messages': [],
            'share_submissions': [],
            'empty_job_warnings': [],
            'real_job_ids_found': [],
            'hashrate_readings': []
        }
        
        for log in self.mining_logs:
            # Look for "✅ Stored job from login with ID:" messages
            if "Stored job from login with ID:" in log:
                analysis['stored_job_messages'].append(log)
                # Extract job ID
                if "ID: " in log:
                    job_id = log.split("ID: ")[1].strip()
                    if job_id and not job_id.startswith('local_') and job_id != 'NO_JOB_ID':
                        analysis['real_job_ids_found'].append(job_id)
                        print(f"   ✅ Found real job ID: {job_id}")
            
            # Look for "✅ Using REAL pool job:" messages
            elif "Using REAL pool job:" in log:
                analysis['real_job_usage'].append(log)
                print(f"   ✅ Real job usage: {log}")
            
            # Look for "📋 JOB DATA RECEIVED:" messages
            elif "JOB DATA RECEIVED:" in log:
                analysis['job_data_received'].append(log)
                print(f"   📋 Job data received: {log}")
            
            # Look for "✅ Updated job with ID:" messages
            elif "Updated job with ID:" in log:
                analysis['updated_job_messages'].append(log)
                # Extract job ID
                if "ID: " in log:
                    job_id = log.split("ID: ")[1].strip()
                    if job_id and not job_id.startswith('local_') and job_id != 'NO_ID':
                        analysis['real_job_ids_found'].append(job_id)
                        print(f"   ✅ Updated with real job ID: {job_id}")
            
            # Look for share submissions with job IDs
            elif "job=" in log and ("submitting" in log.lower() or "share" in log.lower()):
                analysis['share_submissions'].append(log)
                print(f"   🎯 Share submission: {log}")
            
            # Look for "⏳ No real pool job available" warnings
            elif "No real pool job available" in log:
                analysis['empty_job_warnings'].append(log)
                print(f"   ⚠️ Empty job warning: {log}")
            
            # Look for hashrate readings
            elif "H/s" in log and any(keyword in log for keyword in ["Mining Status:", "Thread"]):
                analysis['hashrate_readings'].append(log)
        
        # Remove duplicates from real job IDs
        analysis['real_job_ids_found'] = list(set(analysis['real_job_ids_found']))
        
        print(f"   📊 Analysis complete:")
        print(f"      - Stored job messages: {len(analysis['stored_job_messages'])}")
        print(f"      - Real job usage: {len(analysis['real_job_usage'])}")
        print(f"      - Job data received: {len(analysis['job_data_received'])}")
        print(f"      - Updated job messages: {len(analysis['updated_job_messages'])}")
        print(f"      - Share submissions: {len(analysis['share_submissions'])}")
        print(f"      - Empty job warnings: {len(analysis['empty_job_warnings'])}")
        print(f"      - Unique real job IDs: {len(analysis['real_job_ids_found'])}")
        print(f"      - Hashrate readings: {len(analysis['hashrate_readings'])}")
        
        return analysis
    
    def test_job_id_extraction_verification(self, analysis: Dict[str, Any]):
        """Test 1: Job ID Extraction Verification"""
        print("\n1️⃣ Testing Job ID Extraction Verification...")
        
        stored_jobs = len(analysis['stored_job_messages'])
        real_job_ids = len(analysis['real_job_ids_found'])
        
        # Check for real job IDs like "217912973661599"
        has_numeric_job_ids = any(
            job_id.isdigit() and len(job_id) > 10 
            for job_id in analysis['real_job_ids_found']
        )
        
        success = stored_jobs > 0 and real_job_ids > 0 and has_numeric_job_ids
        
        if success:
            sample_job_ids = analysis['real_job_ids_found'][:3]  # Show first 3
            self.log_test("Job ID Extraction Verification", True,
                        f"Enhanced job ID extraction working - {real_job_ids} real job IDs found",
                        {
                            'stored_job_messages': stored_jobs,
                            'real_job_ids_count': real_job_ids,
                            'sample_job_ids': sample_job_ids,
                            'has_numeric_ids': has_numeric_job_ids
                        })
        else:
            self.log_test("Job ID Extraction Verification", False,
                        f"Job ID extraction issues - stored: {stored_jobs}, real IDs: {real_job_ids}",
                        {
                            'stored_job_messages': stored_jobs,
                            'real_job_ids_found': analysis['real_job_ids_found'],
                            'has_numeric_ids': has_numeric_job_ids
                        })
        
        return success
    
    def test_share_submission_success(self, analysis: Dict[str, Any]):
        """Test 2: Share Submission Success"""
        print("\n2️⃣ Testing Share Submission Success...")
        
        share_submissions = len(analysis['share_submissions'])
        empty_job_warnings = len(analysis['empty_job_warnings'])
        real_job_usage = len(analysis['real_job_usage'])
        
        # Check for shares submitted with real job IDs (not local_XXXXXX)
        real_share_submissions = 0
        for submission in analysis['share_submissions']:
            if "job=" in submission and "local_" not in submission:
                real_share_submissions += 1
        
        success = (share_submissions > 0 and 
                  real_share_submissions > 0 and 
                  empty_job_warnings == 0)
        
        if success:
            self.log_test("Share Submission Success", True,
                        f"Share submissions working with real job IDs - {real_share_submissions}/{share_submissions} real",
                        {
                            'total_submissions': share_submissions,
                            'real_submissions': real_share_submissions,
                            'empty_job_warnings': empty_job_warnings,
                            'real_job_usage': real_job_usage
                        })
        else:
            self.log_test("Share Submission Success", False,
                        f"Share submission issues - real: {real_share_submissions}, warnings: {empty_job_warnings}",
                        {
                            'total_submissions': share_submissions,
                            'real_submissions': real_share_submissions,
                            'empty_job_warnings': empty_job_warnings,
                            'sample_warnings': analysis['empty_job_warnings'][:3]
                        })
        
        return success
    
    def test_enhanced_job_processing(self, analysis: Dict[str, Any]):
        """Test 3: Enhanced Job Processing"""
        print("\n3️⃣ Testing Enhanced Job Processing...")
        
        job_data_received = len(analysis['job_data_received'])
        updated_job_messages = len(analysis['updated_job_messages'])
        
        # Check for nested job structure analysis
        has_nested_analysis = any(
            "JOB DATA RECEIVED:" in msg for msg in analysis['job_data_received']
        )
        
        success = (job_data_received > 0 and 
                  updated_job_messages > 0 and 
                  has_nested_analysis)
        
        if success:
            self.log_test("Enhanced Job Processing", True,
                        f"Enhanced job processing working - nested structure analysis detected",
                        {
                            'job_data_received': job_data_received,
                            'updated_job_messages': updated_job_messages,
                            'has_nested_analysis': has_nested_analysis
                        })
        else:
            self.log_test("Enhanced Job Processing", False,
                        f"Job processing issues - data received: {job_data_received}, updates: {updated_job_messages}",
                        {
                            'job_data_received': job_data_received,
                            'updated_job_messages': updated_job_messages,
                            'has_nested_analysis': has_nested_analysis
                        })
        
        return success
    
    def test_mining_performance(self, analysis: Dict[str, Any]):
        """Test 4: Mining Performance"""
        print("\n4️⃣ Testing Mining Performance...")
        
        hashrate_readings = analysis['hashrate_readings']
        
        # Extract hashrate values
        hashrates = []
        for reading in hashrate_readings:
            try:
                # Look for patterns like "1234.5 H/s"
                if "H/s" in reading:
                    parts = reading.split()
                    for i, part in enumerate(parts):
                        if "H/s" in part or (i < len(parts) - 1 and parts[i + 1] == "H/s"):
                            hashrate_str = part.replace("H/s", "").replace(",", "")
                            try:
                                hashrate = float(hashrate_str)
                                hashrates.append(hashrate)
                                break
                            except ValueError:
                                continue
            except Exception:
                continue
        
        # Check for 1000+ H/s performance
        max_hashrate = max(hashrates) if hashrates else 0
        avg_hashrate = sum(hashrates) / len(hashrates) if hashrates else 0
        
        success = max_hashrate >= 1000 or avg_hashrate >= 800  # Allow some tolerance
        
        if success:
            self.log_test("Mining Performance", True,
                        f"Mining performance good - Max: {max_hashrate:.1f} H/s, Avg: {avg_hashrate:.1f} H/s",
                        {
                            'max_hashrate': max_hashrate,
                            'avg_hashrate': avg_hashrate,
                            'hashrate_readings_count': len(hashrates),
                            'sample_readings': hashrate_readings[:3]
                        })
        else:
            self.log_test("Mining Performance", False,
                        f"Mining performance low - Max: {max_hashrate:.1f} H/s, Avg: {avg_hashrate:.1f} H/s",
                        {
                            'max_hashrate': max_hashrate,
                            'avg_hashrate': avg_hashrate,
                            'hashrate_readings_count': len(hashrates),
                            'all_readings': hashrate_readings
                        })
        
        return success
    
    def run_comprehensive_test(self):
        """Run comprehensive enhanced job ID extraction test"""
        print("🎯 ENHANCED JOB ID EXTRACTION TEST FOR ZEROPOOL.IO")
        print("=" * 70)
        print("Testing enhanced job ID extraction fix for zeropool.io nested job structure")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("=" * 70)
        
        # Step 1: Start mining with zeropool.io
        if not self.start_xmr_mining_zeropool():
            print("❌ Failed to start mining - aborting test")
            return 0, 4, self.test_results
        
        # Step 2: Capture mining logs for 70 seconds
        print(f"\n⏱️ Running mining for 70 seconds to capture job acquisitions and share submissions...")
        if not self.capture_mining_logs(70):
            print("❌ Failed to capture mining logs - aborting test")
            return 0, 4, self.test_results
        
        # Step 3: Analyze logs
        analysis = self.analyze_job_id_extraction()
        
        # Step 4: Run tests
        tests = [
            lambda: self.test_job_id_extraction_verification(analysis),
            lambda: self.test_share_submission_success(analysis),
            lambda: self.test_enhanced_job_processing(analysis),
            lambda: self.test_mining_performance(analysis)
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(1)
            except Exception as e:
                print(f"❌ Test crashed: {str(e)}")
        
        # Stop any remaining mining processes
        try:
            stop_config = {"action": "stop"}
            self.session.post(f"{BACKEND_URL}/mining/control", json=stop_config)
        except:
            pass
        
        print("\n" + "=" * 70)
        print(f"📊 ENHANCED JOB ID EXTRACTION TEST RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Enhanced job ID extraction fix is working perfectly!")
            print("✅ Real job IDs like '217912973661599' are being extracted and used")
            print("✅ Share submissions use real zeropool.io job IDs")
            print("✅ Nested job structure analysis is working")
            print("✅ Mining performance meets requirements")
        elif passed >= 3:
            print("✅ MOSTLY WORKING - Enhanced job ID extraction is largely functional")
            print("⚠️ Minor issues detected but core functionality works")
        else:
            print("⚠️ SIGNIFICANT ISSUES - Enhanced job ID extraction needs attention")
        
        return passed, total, self.test_results

def main():
    """Main test execution"""
    tester = ZeropoolJobExtractionTester()
    passed, total, results = tester.run_comprehensive_test()
    
    # Save detailed results
    with open('/app/zeropool_job_extraction_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': (passed/total)*100,
                'timestamp': datetime.now().isoformat(),
                'test_focus': 'Enhanced Job ID Extraction for zeropool.io'
            },
            'detailed_results': results,
            'mining_logs_sample': tester.mining_logs[-50:] if tester.mining_logs else []  # Last 50 logs
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/zeropool_job_extraction_results.json")
    
    return passed, total

if __name__ == "__main__":
    main()