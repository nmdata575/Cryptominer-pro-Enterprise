"""
CryptoMiner Enterprise V30 - License System
Generates and validates 5000 enterprise license keys
"""

import random
import string
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class EnterpriseV30License:
    def __init__(self):
        self.license_file = "/app/backend/enterprise_licenses.json"
        self.activated_licenses = "/app/backend/activated_licenses.json"
        self.key_length = 42
        self.total_keys = 5000
        
    def generate_license_key(self) -> str:
        """Generate a single 42-character alphanumeric license key"""
        # Format: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXXX (42 chars total)
        chars = string.ascii_uppercase + string.digits
        
        segments = []
        segments.append(''.join(random.choices(chars, k=5)))  # 5 chars
        segments.append(''.join(random.choices(chars, k=5)))  # 5 chars
        segments.append(''.join(random.choices(chars, k=5)))  # 5 chars
        segments.append(''.join(random.choices(chars, k=5)))  # 5 chars
        segments.append(''.join(random.choices(chars, k=5)))  # 5 chars
        segments.append(''.join(random.choices(chars, k=5)))  # 5 chars
        segments.append(''.join(random.choices(chars, k=6)))  # 6 chars
        
        return '-'.join(segments)
    
    def generate_license_database(self) -> Dict:
        """Generate 5000 unique enterprise license keys"""
        print("🔑 Generating 5000 Enterprise License Keys for CryptoMiner V30...")
        
        licenses = {}
        generated_keys = set()
        
        # Generate keys ensuring uniqueness
        while len(generated_keys) < self.total_keys:
            key = self.generate_license_key()
            if key not in generated_keys:
                generated_keys.add(key)
                
                # Create license entry with metadata
                licenses[key] = {
                    "key": key,
                    "type": "enterprise",
                    "version": "v30",
                    "features": [
                        "distributed_mining",
                        "gpu_mining",
                        "unlimited_nodes", 
                        "central_control",
                        "premium_support",
                        "advanced_analytics"
                    ],
                    "max_nodes": -1,  # unlimited
                    "max_gpu_count": -1,  # unlimited
                    "max_cpu_cores": -1,  # unlimited
                    "generated_date": datetime.now().isoformat(),
                    "expires": (datetime.now() + timedelta(days=365*10)).isoformat(),  # 10 years
                    "activated": False,
                    "activation_date": None,
                    "activated_by": None,
                    "node_registrations": []
                }
        
        license_data = {
            "version": "v30",
            "total_keys": len(licenses),
            "generated_date": datetime.now().isoformat(),
            "licenses": licenses
        }
        
        # Save to file
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f, indent=2)
        
        print(f"✅ Successfully generated {len(licenses)} license keys")
        print(f"📁 Saved to: {self.license_file}")
        
        # Display first 10 keys as sample
        sample_keys = list(licenses.keys())[:10]
        print(f"\n📋 Sample License Keys:")
        for i, key in enumerate(sample_keys, 1):
            print(f"   {i:2d}. {key}")
        print(f"   ... and {len(licenses) - 10} more keys")
        
        return license_data
    
    def validate_license(self, license_key: str) -> Dict:
        """Validate an enterprise license key"""
        try:
            if not os.path.exists(self.license_file):
                return {"valid": False, "error": "License database not found"}
            
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            if license_key not in license_data["licenses"]:
                return {"valid": False, "error": "Invalid license key"}
            
            license_info = license_data["licenses"][license_key]
            
            # Check expiration
            expires = datetime.fromisoformat(license_info["expires"])
            if datetime.now() > expires:
                return {"valid": False, "error": "License expired"}
            
            return {
                "valid": True,
                "license": license_info,
                "features": license_info["features"],
                "max_nodes": license_info["max_nodes"],
                "enterprise": True
            }
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def activate_license(self, license_key: str, node_info: Dict) -> Dict:
        """Activate an enterprise license"""
        validation = self.validate_license(license_key)
        if not validation["valid"]:
            return validation
        
        try:
            # Load license data
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Update activation status
            license_data["licenses"][license_key]["activated"] = True
            license_data["licenses"][license_key]["activation_date"] = datetime.now().isoformat()
            license_data["licenses"][license_key]["activated_by"] = node_info
            
            # Save updated data
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
            
            # Track activated licenses
            activated_data = {"activated_licenses": {}, "activation_history": []}
            if os.path.exists(self.activated_licenses):
                with open(self.activated_licenses, 'r') as f:
                    activated_data = json.load(f)
            
            activated_data["activated_licenses"][license_key] = {
                "activation_date": datetime.now().isoformat(),
                "node_info": node_info,
                "features": validation["license"]["features"]
            }
            
            activated_data["activation_history"].append({
                "license_key": license_key,
                "activation_date": datetime.now().isoformat(),
                "node_info": node_info
            })
            
            with open(self.activated_licenses, 'w') as f:
                json.dump(activated_data, f, indent=2)
            
            return {
                "valid": True,
                "activated": True,
                "message": "Enterprise license activated successfully",
                "features": validation["license"]["features"]
            }
            
        except Exception as e:
            return {"valid": False, "error": f"Activation error: {str(e)}"}

# Generate the license keys when this module is run
if __name__ == "__main__":
    license_system = EnterpriseV30License()
    license_data = license_system.generate_license_database()
    
    # Test a few keys
    sample_keys = list(license_data["licenses"].keys())[:3]
    print(f"\n🧪 Testing License Validation:")
    
    for key in sample_keys:
        result = license_system.validate_license(key)
        print(f"   Key: {key}")
        print(f"   Valid: {result['valid']}")
        if result["valid"]:
            print(f"   Features: {len(result['features'])} enterprise features")
        print()