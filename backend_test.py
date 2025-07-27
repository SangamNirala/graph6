#!/usr/bin/env python3
"""
Backend API Testing for AI Business Video Script & Voiceover Generator
FOCUS: Testing external URL routing issue with 502 Bad Gateway errors
Tests all API endpoints including Groq integration for script generation
"""

import requests
import json
import os
import sys
from datetime import datetime

# Get base URL from environment or use default
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://c3e452ad-dd72-4b8e-8fa3-52419b0ec11f.preview.emergentagent.com')
EXTERNAL_API_BASE = f"{BASE_URL}/api"

# Internal testing URL
INTERNAL_API_BASE = "http://localhost:3000/api"

class BackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.external_working = False
        self.internal_working = False
        
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
    
    def test_internal_api_root(self):
        """Test internal API root endpoint"""
        try:
            response = requests.get(f"{INTERNAL_API_BASE}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "AI Business Video Script & Voiceover Generator API" in data.get("message", ""):
                    self.log_result("Internal API Root", "PASS", "Internal API root endpoint working correctly")
                    self.internal_working = True
                    return True
                else:
                    self.log_result("Internal API Root", "FAIL", "Unexpected response message", data)
                    return False
            else:
                self.log_result("Internal API Root", "FAIL", f"HTTP {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_result("Internal API Root", "FAIL", "Connection error", str(e))
            return False
    
    def test_external_api_root(self):
        """Test external API root endpoint - this should reveal the 502 issue"""
        try:
            response = requests.get(f"{EXTERNAL_API_BASE}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "AI Business Video Script & Voiceover Generator API" in data.get("message", ""):
                    self.log_result("External API Root", "PASS", "External API root endpoint working correctly")
                    self.external_working = True
                    return True
                else:
                    self.log_result("External API Root", "FAIL", "Unexpected response message", data)
                    return False
            elif response.status_code == 502:
                self.log_result("External API Root", "FAIL", "502 Bad Gateway - Kubernetes ingress routing issue confirmed", response.text[:200])
                return False
            else:
                self.log_result("External API Root", "FAIL", f"HTTP {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_result("External API Root", "FAIL", "Connection error", str(e))
            return False
    
    def test_internal_generate_script(self):
        """Test internal script generation endpoint"""
        test_prompt = "AI-powered customer relationship management software that helps small businesses automate their sales processes and increase revenue by 40%"
        
        try:
            payload = {
                "prompt": test_prompt,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
            
            response = requests.post(
                f"{INTERNAL_API_BASE}/generate-script",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "script" in data and data["script"]:
                    script_content = data["script"]
                    # Check if script contains business-relevant content
                    if any(keyword in script_content.lower() for keyword in ["crm", "sales", "business", "conversion"]):
                        self.log_result("Internal Script Generation", "PASS", 
                                      f"Script generated successfully ({len(script_content)} characters)")
                        print(f"   Generated script preview: {script_content[:100]}...")
                        return True, script_content
                    else:
                        self.log_result("Internal Script Generation", "FAIL", 
                                      "Script generated but doesn't seem relevant to prompt", script_content[:200])
                        return False, ""
                else:
                    self.log_result("Internal Script Generation", "FAIL", 
                                  "No script in response", data)
                    return False, ""
            else:
                error_msg = response.text
                if response.status_code == 500:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", error_msg)
                    except:
                        pass
                self.log_result("Internal Script Generation", "FAIL", 
                              f"HTTP {response.status_code}: {error_msg}")
                return False, ""
                
        except Exception as e:
            self.log_result("Internal Script Generation", "FAIL", "Request error", str(e))
            return False, ""
    
    def test_external_generate_script(self):
        """Test external script generation endpoint - this should reveal the 502 issue"""
        test_prompt = "AI-powered customer relationship management software that helps small businesses automate their sales processes and increase revenue by 40%"
        
        try:
            payload = {
                "prompt": test_prompt,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
            
            response = requests.post(
                f"{EXTERNAL_API_BASE}/generate-script",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "script" in data and data["script"]:
                    script_content = data["script"]
                    # Check if script contains business-relevant content
                    if any(keyword in script_content.lower() for keyword in ["crm", "sales", "business", "conversion"]):
                        self.log_result("External Script Generation", "PASS", 
                                      f"Script generated successfully ({len(script_content)} characters)")
                        return True, script_content
                    else:
                        self.log_result("External Script Generation", "FAIL", 
                                      "Script generated but doesn't seem relevant to prompt", script_content[:200])
                        return False, ""
                else:
                    self.log_result("External Script Generation", "FAIL", 
                                  "No script in response", data)
                    return False, ""
            elif response.status_code == 502:
                self.log_result("External Script Generation", "FAIL", "502 Bad Gateway - Kubernetes ingress routing issue confirmed", response.text[:200])
                return False, ""
            else:
                error_msg = response.text
                if response.status_code == 500:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", error_msg)
                    except:
                        pass
                self.log_result("External Script Generation", "FAIL", 
                              f"HTTP {response.status_code}: {error_msg}")
                return False, ""
                
        except Exception as e:
            self.log_result("External Script Generation", "FAIL", "Request error", str(e))
            return False, ""
    
    def test_internal_generate_voiceover(self):
        """Test internal voiceover generation endpoint"""
        try:
            payload = {
                "text": "This is a test script for voiceover generation.",
                "voice_style": "professional"
            }
            
            response = requests.post(
                f"{INTERNAL_API_BASE}/generate-voiceover",
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
                        self.log_result("Internal Voiceover Generation", "PASS", 
                                      f"Audio generated successfully ({audio_size} bytes)")
                        return True
                    else:
                        self.log_result("Internal Voiceover Generation", "FAIL", 
                                      "Empty audio response")
                        return False
                else:
                    self.log_result("Internal Voiceover Generation", "FAIL", 
                                  f"Wrong content type: {content_type}")
                    return False
            else:
                self.log_result("Internal Voiceover Generation", "FAIL", 
                              f"HTTP {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_result("Internal Voiceover Generation", "FAIL", "Request error", str(e))
            return False
    
    def test_external_generate_voiceover(self):
        """Test external voiceover generation endpoint - this should reveal the 502 issue"""
        try:
            payload = {
                "text": "This is a test script for voiceover generation.",
                "voice_style": "professional"
            }
            
            response = requests.post(
                f"{EXTERNAL_API_BASE}/generate-voiceover",
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
                        self.log_result("External Voiceover Generation", "PASS", 
                                      f"Audio generated successfully ({audio_size} bytes)")
                        return True
                    else:
                        self.log_result("External Voiceover Generation", "FAIL", 
                                      "Empty audio response")
                        return False
                else:
                    self.log_result("External Voiceover Generation", "FAIL", 
                                  f"Wrong content type: {content_type}")
                    return False
            elif response.status_code == 502:
                self.log_result("External Voiceover Generation", "FAIL", "502 Bad Gateway - Kubernetes ingress routing issue confirmed", response.text[:200])
                return False
            else:
                self.log_result("External Voiceover Generation", "FAIL", 
                              f"HTTP {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_result("External Voiceover Generation", "FAIL", "Request error", str(e))
            return False
    
    def test_internal_scripts_history(self):
        """Test internal scripts history endpoint"""
        try:
            response = requests.get(f"{INTERNAL_API_BASE}/scripts", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Internal Scripts History", "PASS", 
                                  f"Retrieved {len(data)} script records")
                    return True
                else:
                    self.log_result("Internal Scripts History", "FAIL", 
                                  "Response is not a list", type(data))
                    return False
            else:
                self.log_result("Internal Scripts History", "FAIL", 
                              f"HTTP {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_result("Internal Scripts History", "FAIL", "Request error", str(e))
            return False
    
    def test_external_scripts_history(self):
        """Test external scripts history endpoint - this should reveal the 502 issue"""
        try:
            response = requests.get(f"{EXTERNAL_API_BASE}/scripts", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("External Scripts History", "PASS", 
                                  f"Retrieved {len(data)} script records")
                    return True
                else:
                    self.log_result("External Scripts History", "FAIL", 
                                  "Response is not a list", type(data))
                    return False
            elif response.status_code == 502:
                self.log_result("External Scripts History", "FAIL", "502 Bad Gateway - Kubernetes ingress routing issue confirmed", response.text[:200])
                return False
            else:
                self.log_result("External Scripts History", "FAIL", 
                              f"HTTP {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_result("External Scripts History", "FAIL", "Request error", str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling scenarios using internal API"""
        # Test missing prompt parameter
        try:
            response = requests.post(
                f"{INTERNAL_API_BASE}/generate-script",
                json={},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 400
            if success:
                data = response.json()
                success = "error" in data and "required" in data["error"].lower()
            
            details = f"Status: {response.status_code}, Response: {response.text[:100]}"
            self.log_result("Missing Prompt Validation", "PASS" if success else "FAIL", 
                          "Properly validates missing prompt" if success else "Validation failed", details)
            
        except Exception as e:
            self.log_result("Missing Prompt Validation", "FAIL", "Exception occurred", str(e))
        
        # Test invalid route
        try:
            response = requests.get(f"{INTERNAL_API_BASE}/invalid-route", timeout=10)
            success = response.status_code == 404
            details = f"Status: {response.status_code}, Response: {response.text[:100]}"
            self.log_result("Invalid Route Handling", "PASS" if success else "FAIL", 
                          "Properly returns 404 for invalid routes" if success else "404 handling failed", details)
            
        except Exception as e:
            self.log_result("Invalid Route Handling", "FAIL", "Exception occurred", str(e))
    
    def test_groq_api_integration(self):
        """Test Groq API integration specifically using internal endpoint"""
        test_payload = {
            "prompt": "Revolutionary fintech startup that uses blockchain technology to provide instant cross-border payments with zero fees"
        }
        
        try:
            response = requests.post(
                f"{INTERNAL_API_BASE}/generate-script",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                script = data.get("script", "")
                
                # Check if script contains business-relevant keywords
                business_keywords = ["fintech", "blockchain", "payments", "fees", "technology", "instant", "cross-border"]
                keyword_matches = sum(1 for keyword in business_keywords if keyword.lower() in script.lower())
                
                success = len(script) > 500 and keyword_matches >= 3
                details = f"Status: {response.status_code}, Script length: {len(script)} chars, Keywords matched: {keyword_matches}/7"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                
            self.log_result("Groq API Integration", "PASS" if success else "FAIL", 
                          "Groq API working correctly" if success else "Groq API integration failed", details)
            return success
            
        except Exception as e:
            self.log_result("Groq API Integration", "FAIL", "Exception occurred", str(e))
            return False
    
    def test_mongodb_storage(self):
        """Test MongoDB storage using internal endpoint"""
        try:
            # First generate a script with a unique identifier
            test_prompt = f"Test script generation for MongoDB storage verification - {datetime.now().isoformat()}"
            
            response = requests.post(
                f"{INTERNAL_API_BASE}/generate-script",
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
            history_response = requests.get(f"{INTERNAL_API_BASE}/scripts", timeout=10)
            
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
        """Run all backend tests focusing on external URL routing issue"""
        print(f"🚀 Starting Backend API Tests - External URL Routing Issue Investigation")
        print(f"External URL: {EXTERNAL_API_BASE}")
        print(f"Internal URL: {INTERNAL_API_BASE}")
        print("=" * 80)
        
        # Test internal API first (should work)
        print(f"\n{'🔧 INTERNAL API TESTS (Expected to work)':=^80}")
        internal_tests = []
        internal_tests.append(self.test_internal_api_root())
        script_success, generated_script = self.test_internal_generate_script()
        internal_tests.append(script_success)
        internal_tests.append(self.test_internal_generate_voiceover())
        internal_tests.append(self.test_internal_scripts_history())
        
        # Test external API (expected to fail with 502)
        print(f"\n{'🌐 EXTERNAL API TESTS (Expected to fail with 502)':=^80}")
        external_tests = []
        external_tests.append(self.test_external_api_root())
        script_success_ext, _ = self.test_external_generate_script()
        external_tests.append(script_success_ext)
        external_tests.append(self.test_external_generate_voiceover())
        external_tests.append(self.test_external_scripts_history())
        
        # Additional tests using internal API
        print(f"\n{'🛠️ ADDITIONAL TESTS (Using Internal API)':=^80}")
        self.test_error_handling()
        groq_success = self.test_groq_api_integration()
        mongodb_success = self.test_mongodb_storage()
        
        # Summary
        print(f"\n{'📊 TEST SUMMARY':=^80}")
        internal_passed = sum(internal_tests)
        external_passed = sum(external_tests)
        
        print(f"Internal API Tests: {internal_passed}/{len(internal_tests)} passed")
        print(f"External API Tests: {external_passed}/{len(external_tests)} passed")
        print(f"Groq API Integration: {'✅ Working' if groq_success else '❌ Failed'}")
        print(f"MongoDB Storage: {'✅ Working' if mongodb_success else '❌ Failed'}")
        
        # Diagnosis
        print(f"\n{'🔍 DIAGNOSIS':=^80}")
        if internal_passed == len(internal_tests) and external_passed == 0:
            print("✅ CONFIRMED: Backend API is working internally")
            print("❌ CONFIRMED: External URL routing is failing (likely 502 Bad Gateway)")
            print("🔧 ISSUE: Kubernetes ingress not properly routing /api/* requests")
            print("💡 SOLUTION NEEDED: Fix ingress configuration for /api path routing")
        elif internal_passed == len(internal_tests) and external_passed > 0:
            print("✅ Backend API working both internally and externally")
            print("🎉 No routing issues detected")
        else:
            print("❌ Backend API has internal issues that need to be resolved first")
        
        print(f"\n{'🏁 TEST COMPLETED':=^80}")
        return self.passed_tests, self.failed_tests, self.results

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(0 if failed == 0 else 1)