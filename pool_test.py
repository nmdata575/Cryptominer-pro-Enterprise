#!/usr/bin/env python3
"""
Test Pool Connection Directly
Test if we can connect to the EFL pool directly
"""

import socket
import json
import time

def test_pool_connection():
    """Test direct connection to EFL pool"""
    pool_host = "stratum.luckydogpool.com"
    pool_port = 7026
    
    print(f"🌐 Testing connection to {pool_host}:{pool_port}")
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        # Connect
        print("   Connecting...")
        start_time = time.time()
        sock.connect((pool_host, pool_port))
        connection_time = time.time() - start_time
        print(f"   ✅ Connected in {connection_time:.3f}s")
        
        # Send mining.subscribe
        subscribe_msg = {
            "id": 1,
            "method": "mining.subscribe",
            "params": ["CryptoMiner-V30/1.0", None]
        }
        
        msg_json = json.dumps(subscribe_msg) + '\n'
        print(f"   Sending: {subscribe_msg}")
        sock.send(msg_json.encode('utf-8'))
        
        # Receive response
        print("   Waiting for response...")
        data = sock.recv(4096).decode('utf-8').strip()
        print(f"   Received: {data}")
        
        if data:
            try:
                response = json.loads(data)
                if 'result' in response:
                    print("   ✅ Pool responded with valid JSON")
                    result = response['result']
                    if len(result) >= 3:
                        extranonce1 = result[1]
                        extranonce2_size = result[2]
                        print(f"   📋 Extranonce1: {extranonce1}")
                        print(f"   📋 Extranonce2 size: {extranonce2_size}")
                        
                        # Send mining.authorize
                        authorize_msg = {
                            "id": 2,
                            "method": "mining.authorize",
                            "params": ["LaEni1U9jb4A38frAbjj3UHMzM6vrre8Dd", "x"]
                        }
                        
                        msg_json = json.dumps(authorize_msg) + '\n'
                        print(f"   Sending: {authorize_msg}")
                        sock.send(msg_json.encode('utf-8'))
                        
                        # Receive auth response
                        auth_data = sock.recv(4096).decode('utf-8').strip()
                        print(f"   Auth response: {auth_data}")
                        
                        if auth_data:
                            auth_response = json.loads(auth_data)
                            if auth_response.get('result') == True:
                                print("   ✅ Successfully authorized with pool!")
                                return True
                            else:
                                print(f"   ❌ Authorization failed: {auth_response}")
                                return False
                    else:
                        print("   ❌ Invalid subscribe response format")
                        return False
                else:
                    print(f"   ❌ Pool error: {response}")
                    return False
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON response: {e}")
                return False
        else:
            print("   ❌ No response from pool")
            return False
            
    except socket.timeout:
        print("   ❌ Connection timeout")
        return False
    except ConnectionRefusedError:
        print("   ❌ Connection refused")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass

if __name__ == "__main__":
    success = test_pool_connection()
    if success:
        print("\n🎉 Pool connection test successful!")
        print("✅ EFL pool is accessible and responding correctly")
    else:
        print("\n❌ Pool connection test failed!")
        print("❌ Cannot establish proper connection to EFL pool")