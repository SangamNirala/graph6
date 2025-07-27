#!/usr/bin/env python3
"""
Backend API Testing for AI Business Video Script & Voiceover Generator
Tests all API endpoints including Groq integration for script generation
"""

import requests
import json
import os
import sys
from datetime import datetime

# Get base URL from environment or use default
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://2dee0019-5bcc-4c2d-9ae6-38ca6d3f5e42.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

# For testing, use localhost if external URL fails
LOCALHOST_API = "http://localhost:3000/api"

class BackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.api_base = API_BASE
        self.using_localhost = False
        
    def check_api_connectivity(self):
        """Check if API is accessible and switch to localhost if needed"""
        try:
            response = requests.get(f"{API_BASE}", timeout=5)
            if response.status_code in [200, 404]:  # Any valid response
                return API_BASE
        except:
            pass
        
        # Try localhost
        try:
            response = requests.get(f"{LOCALHOST_API}", timeout=5)
            if response.status_code in [200, 404]:
                self.using_localhost = True
                print(f"⚠️  External URL not accessible, using localhost for testing")
                return LOCALHOST_API
        except:
            pass
        
        return API_BASE  # Return original if both fail
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
        
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.api_base}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "AI Business Video Script & Voiceover Generator API" in data.get("message", ""):
                    self.log_result("Root Endpoint", "PASS", "Root endpoint working correctly")
                    return True
                else:
                    self.log_result("Root Endpoint", "FAIL", "Unexpected response message", data)
                    return False
            else:
                self.log_result("Root Endpoint", "FAIL", f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Root Endpoint", "FAIL", "Connection error", str(e))
            return False
    
    def test_script_generation(self):
        """Test the critical Groq integration for script generation"""
        test_prompt = "We're launching a new AI-powered CRM software that helps sales teams automate their follow-ups and increase conversion rates by 40%. Our target audience is small to medium businesses looking to scale their sales operations efficiently."
        
        try:
            payload = {
                "prompt": test_prompt,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
            
            response = requests.post(
                f"{API_BASE}/generate-script",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30  # Groq API might take some time
            )
            
            if response.status_code == 200:
                data = response.json()
                if "script" in data and data["script"]:
                    script_content = data["script"]
                    # Check if script contains business-relevant content
                    if any(keyword in script_content.lower() for keyword in ["crm", "sales", "business", "conversion"]):
                        self.log_result("Script Generation (Groq)", "PASS", 
                                      f"Script generated successfully ({len(script_content)} characters)")
                        print(f"   Generated script preview: {script_content[:100]}...")
                        return True
                    else:
                        self.log_result("Script Generation (Groq)", "FAIL", 
                                      "Script generated but doesn't seem relevant to prompt", script_content[:200])
                        return False
                else:
                    self.log_result("Script Generation (Groq)", "FAIL", 
                                  "No script in response", data)
                    return False
            else:
                error_msg = response.text
                if response.status_code == 500:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", error_msg)
                    except:
                        pass
                self.log_result("Script Generation (Groq)", "FAIL", 
                              f"HTTP {response.status_code}: {error_msg}")
                return False
                
        except Exception as e:
            self.log_result("Script Generation (Groq)", "FAIL", "Request error", str(e))
            return False
    
    def test_script_generation_validation(self):
        """Test script generation endpoint validation"""
        try:
            # Test missing prompt
            response = requests.post(
                f"{API_BASE}/generate-script",
                json={},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                if "error" in data and "required" in data["error"].lower():
                    self.log_result("Script Generation Validation", "PASS", 
                                  "Properly validates missing prompt")
                    return True
                else:
                    self.log_result("Script Generation Validation", "FAIL", 
                                  "Wrong error message for missing prompt", data)
                    return False
            else:
                self.log_result("Script Generation Validation", "FAIL", 
                              f"Expected 400, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Script Generation Validation", "FAIL", "Request error", str(e))
            return False
    
    def test_voiceover_generation(self):
        """Test voiceover generation (mock implementation)"""
        try:
            payload = {
                "text": "This is a test script for voiceover generation.",
                "voice_style": "professional"
            }
            
            response = requests.post(
                f"{API_BASE}/generate-voiceover",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                # Check if response is audio data
                content_type = response.headers.get('content-type', '')
                if 'audio/wav' in content_type:
                    audio_size = len(response.content)
                    if audio_size > 0:
                        self.log_result("Voiceover Generation", "PASS", 
                                      f"Audio generated successfully ({audio_size} bytes)")
                        return True
                    else:
                        self.log_result("Voiceover Generation", "FAIL", 
                                      "Empty audio response")
                        return False
                else:
                    self.log_result("Voiceover Generation", "FAIL", 
                                  f"Wrong content type: {content_type}")
                    return False
            else:
                self.log_result("Voiceover Generation", "FAIL", 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Voiceover Generation", "FAIL", "Request error", str(e))
            return False
    
    def test_voiceover_validation(self):
        """Test voiceover generation validation"""
        try:
            # Test missing text
            response = requests.post(
                f"{API_BASE}/generate-voiceover",
                json={},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                if "error" in data and "required" in data["error"].lower():
                    self.log_result("Voiceover Validation", "PASS", 
                                  "Properly validates missing text")
                    return True
                else:
                    self.log_result("Voiceover Validation", "FAIL", 
                                  "Wrong error message for missing text", data)
                    return False
            else:
                self.log_result("Voiceover Validation", "FAIL", 
                              f"Expected 400, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Voiceover Validation", "FAIL", "Request error", str(e))
            return False
    
    def test_scripts_history(self):
        """Test scripts history endpoint"""
        try:
            response = requests.get(f"{API_BASE}/scripts", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Scripts History", "PASS", 
                                  f"Retrieved {len(data)} script records")
                    return True
                else:
                    self.log_result("Scripts History", "FAIL", 
                                  "Response is not a list", type(data))
                    return False
            else:
                self.log_result("Scripts History", "FAIL", 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Scripts History", "FAIL", "Request error", str(e))
            return False
    
    def test_voiceovers_history(self):
        """Test voiceovers history endpoint"""
        try:
            response = requests.get(f"{API_BASE}/voiceovers", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Voiceovers History", "PASS", 
                                  f"Retrieved {len(data)} voiceover records")
                    return True
                else:
                    self.log_result("Voiceovers History", "FAIL", 
                                  "Response is not a list", type(data))
                    return False
            else:
                self.log_result("Voiceovers History", "FAIL", 
                              f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Voiceovers History", "FAIL", "Request error", str(e))
            return False
    
    def test_invalid_route(self):
        """Test that invalid routes return 404"""
        try:
            response = requests.get(f"{API_BASE}/invalid-route", timeout=10)
            
            if response.status_code == 404:
                data = response.json()
                if "error" in data and "not found" in data["error"].lower():
                    self.log_result("Invalid Route", "PASS", 
                                  "Properly returns 404 for invalid routes")
                    return True
                else:
                    self.log_result("Invalid Route", "FAIL", 
                                  "Wrong error message for 404", data)
                    return False
            else:
                self.log_result("Invalid Route", "FAIL", 
                              f"Expected 404, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Invalid Route", "FAIL", "Request error", str(e))
            return False
    
    def test_mongodb_storage(self):
        """Test that data is properly stored in MongoDB by generating a script and checking history"""
        try:
            # First generate a script with a unique identifier
            test_prompt = f"Test script generation for MongoDB storage verification - {datetime.now().isoformat()}"
            
            response = requests.post(
                f"{API_BASE}/generate-script",
                json={"prompt": test_prompt},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_result("MongoDB Storage", "FAIL", 
                              "Could not generate test script for storage verification")
                return False
            
            # Wait a moment for database write
            import time
            time.sleep(1)
            
            # Check if the script appears in history
            history_response = requests.get(f"{API_BASE}/scripts", timeout=10)
            
            if history_response.status_code == 200:
                scripts = history_response.json()
                # Look for our test script in the recent entries
                found = any(script.get("prompt") == test_prompt for script in scripts[:5])
                
                if found:
                    self.log_result("MongoDB Storage", "PASS", 
                                  "Script properly stored and retrieved from MongoDB")
                    return True
                else:
                    self.log_result("MongoDB Storage", "FAIL", 
                                  "Generated script not found in history")
                    return False
            else:
                self.log_result("MongoDB Storage", "FAIL", 
                              "Could not retrieve scripts history for verification")
                return False
                
        except Exception as e:
            self.log_result("MongoDB Storage", "FAIL", "Storage verification error", str(e))
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        # Check connectivity and set API base
        self.api_base = self.check_api_connectivity()
        
        print(f"🚀 Starting Backend API Tests for: {self.api_base}")
        if self.using_localhost:
            print("   (Note: Testing locally due to external URL issues)")
        print("=" * 60)
        
        # Test in order of priority
        tests = [
            ("Basic API Connectivity", self.test_root_endpoint),
            ("Script Generation (CRITICAL - Groq Integration)", self.test_script_generation),
            ("Script Generation Validation", self.test_script_generation_validation),
            ("Voiceover Generation", self.test_voiceover_generation),
            ("Voiceover Validation", self.test_voiceover_validation),
            ("Scripts History", self.test_scripts_history),
            ("Voiceovers History", self.test_voiceovers_history),
            ("Invalid Route Handling", self.test_invalid_route),
            ("MongoDB Storage Verification", self.test_mongodb_storage),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, "FAIL", "Test execution error", str(e))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Show critical failures
        critical_failures = [r for r in self.results if r["status"] == "FAIL" and "CRITICAL" in r["test"]]
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"   - {failure['test']}: {failure['message']}")
        
        return self.passed_tests, self.failed_tests, self.results

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(0 if failed == 0 else 1)