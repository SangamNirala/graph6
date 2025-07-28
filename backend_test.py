#!/usr/bin/env python3
"""
Comprehensive Backend Testing for AI Video Generation Features
Testing the new video generation pipeline with external API integrations
"""

import requests
import json
import base64
import time
import os
from datetime import datetime

# Get base URL from environment
BASE_URL = "https://4657aedc-4483-4596-8e88-942d9f22dc1c.preview.emergentagent.com/api"

# Test business description as specified in requirements
TEST_BUSINESS_DESCRIPTION = "We're launching an innovative AI-powered project management software that helps remote teams collaborate more effectively and increase productivity by 50%. Our solution includes smart task automation, real-time collaboration tools, and predictive analytics for project success."

class VideoGenerationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.generated_script = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "AI Business Video Script" in data.get('message', ''):
                    self.log_result("Root API Endpoint", True, "Root endpoint working correctly")
                    return True
                else:
                    self.log_result("Root API Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("Root API Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Root API Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_script_generation(self):
        """Test script generation to get a script for video generation"""
        try:
            payload = {
                "prompt": TEST_BUSINESS_DESCRIPTION
            }
            
            response = requests.post(f"{self.base_url}/generate-script", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                script = data.get('script', '')
                
                if script and len(script) > 100:
                    self.generated_script = script
                    self.log_result("Script Generation for Video", True, 
                                  f"Generated script successfully ({len(script)} characters)",
                                  {"script_length": len(script), "script_preview": script[:200] + "..."})
                    return True
                else:
                    self.log_result("Script Generation for Video", False, "Script too short or empty")
                    return False
            else:
                self.log_result("Script Generation for Video", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Script Generation for Video", False, f"Request failed: {str(e)}")
            return False

    def test_avatar_image_generation(self):
        """Test avatar image generation using HuggingFace SDXL"""
        try:
            if not self.generated_script:
                self.log_result("Avatar Image Generation", False, "No script available for testing")
                return False
                
            payload = {
                "script": self.generated_script,
                "options": {
                    "avatar_description": "professional business executive",
                    "avatar_style": "realistic"
                }
            }
            
            print("Testing avatar generation (this may take 30-60 seconds)...")
            response = requests.post(f"{self.base_url}/generate-video", json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                video_data = data.get('video', {})
                avatar = video_data.get('avatar', '')
                
                if avatar and len(avatar) > 100:  # Base64 image should be substantial
                    # Verify it's valid base64
                    try:
                        base64.b64decode(avatar)
                        self.log_result("Avatar Image Generation", True, 
                                      f"Avatar generated successfully using HuggingFace SDXL",
                                      {"avatar_size_bytes": len(avatar), "format": "base64"})
                        return True
                    except Exception:
                        self.log_result("Avatar Image Generation", False, "Invalid base64 avatar data")
                        return False
                else:
                    self.log_result("Avatar Image Generation", False, "Avatar data missing or too small")
                    return False
            else:
                self.log_result("Avatar Image Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_result("Avatar Image Generation", False, "Request timed out (>120s)")
            return False
        except Exception as e:
            self.log_result("Avatar Image Generation", False, f"Request failed: {str(e)}")
            return False

    def test_scene_extraction(self):
        """Test scene-based visual prompt extraction using Claude 3.5 Sonnet"""
        try:
            if not self.generated_script:
                self.log_result("Scene-Based Visual Prompt Extraction", False, "No script available for testing")
                return False
                
            payload = {
                "script": self.generated_script
            }
            
            print("Testing scene extraction using Claude 3.5 Sonnet...")
            response = requests.post(f"{self.base_url}/generate-video", json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                video_data = data.get('video', {})
                scenes = video_data.get('scenes', [])
                
                if scenes and len(scenes) >= 3 and len(scenes) <= 5:
                    # Verify scene structure
                    valid_scenes = True
                    for scene in scenes:
                        if not all(key in scene for key in ['timeframe', 'prompt']):
                            valid_scenes = False
                            break
                    
                    if valid_scenes:
                        self.log_result("Scene-Based Visual Prompt Extraction", True, 
                                      f"Extracted {len(scenes)} scene prompts using Claude 3.5 Sonnet",
                                      {"scene_count": len(scenes), "scenes": scenes})
                        return True
                    else:
                        self.log_result("Scene-Based Visual Prompt Extraction", False, "Invalid scene structure")
                        return False
                else:
                    self.log_result("Scene-Based Visual Prompt Extraction", False, 
                                  f"Expected 3-5 scenes, got {len(scenes)}")
                    return False
            else:
                self.log_result("Scene-Based Visual Prompt Extraction", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_result("Scene-Based Visual Prompt Extraction", False, "Request timed out (>120s)")
            return False
        except Exception as e:
            self.log_result("Scene-Based Visual Prompt Extraction", False, f"Request failed: {str(e)}")
            return False

    def test_background_generation(self):
        """Test background image generation using HuggingFace SDXL"""
        try:
            if not self.generated_script:
                self.log_result("Background Image Generation", False, "No script available for testing")
                return False
                
            payload = {
                "script": self.generated_script
            }
            
            print("Testing background generation using HuggingFace SDXL...")
            response = requests.post(f"{self.base_url}/generate-video", json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                video_data = data.get('video', {})
                backgrounds = video_data.get('backgrounds', [])
                
                if backgrounds and len(backgrounds) >= 3:
                    # Verify background structure
                    valid_backgrounds = True
                    for bg in backgrounds:
                        if not all(key in bg for key in ['timeframe', 'prompt', 'image']):
                            valid_backgrounds = False
                            break
                        # Verify base64 image data
                        try:
                            base64.b64decode(bg['image'])
                        except Exception:
                            valid_backgrounds = False
                            break
                    
                    if valid_backgrounds:
                        self.log_result("Background Image Generation", True, 
                                      f"Generated {len(backgrounds)} background images using HuggingFace SDXL",
                                      {"background_count": len(backgrounds)})
                        return True
                    else:
                        self.log_result("Background Image Generation", False, "Invalid background structure or data")
                        return False
                else:
                    self.log_result("Background Image Generation", False, 
                                  f"Expected multiple backgrounds, got {len(backgrounds)}")
                    return False
            else:
                self.log_result("Background Image Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_result("Background Image Generation", False, "Request timed out (>120s)")
            return False
        except Exception as e:
            self.log_result("Background Image Generation", False, f"Request failed: {str(e)}")
            return False

    def test_video_generation_endpoint(self):
        """Test the comprehensive video generation endpoint with 5-step process"""
        try:
            if not self.generated_script:
                self.log_result("Video Generation API Endpoint", False, "No script available for testing")
                return False
                
            payload = {
                "script": self.generated_script,
                "options": {
                    "avatar_description": "professional business executive",
                    "avatar_style": "realistic"
                }
            }
            
            print("Testing complete video generation pipeline (this may take 2-3 minutes)...")
            response = requests.post(f"{self.base_url}/generate-video", json=payload, timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'video' in data:
                    video_data = data['video']
                    processing_steps = video_data.get('processing_steps', [])
                    
                    # Verify all 5 steps completed
                    expected_steps = ['avatar_generation', 'scene_extraction', 'background_generation', 
                                    'talking_head_creation', 'final_composition']
                    
                    completed_steps = [step['name'] for step in processing_steps if step['status'] == 'completed']
                    
                    if len(completed_steps) == 5 and all(step in completed_steps for step in expected_steps):
                        # Verify video data structure
                        required_fields = ['id', 'avatar', 'backgrounds', 'scenes', 'duration', 'videoBase64', 'metadata']
                        if all(field in video_data for field in required_fields):
                            self.log_result("Video Generation API Endpoint", True, 
                                          "Complete 5-step video generation process successful",
                                          {
                                              "steps_completed": len(completed_steps),
                                              "video_id": video_data['id'],
                                              "duration": video_data['duration'],
                                              "scene_count": len(video_data['scenes']),
                                              "background_count": len(video_data['backgrounds'])
                                          })
                            return True
                        else:
                            missing_fields = [f for f in required_fields if f not in video_data]
                            self.log_result("Video Generation API Endpoint", False, 
                                          f"Missing video data fields: {missing_fields}")
                            return False
                    else:
                        self.log_result("Video Generation API Endpoint", False, 
                                      f"Expected 5 steps, completed: {completed_steps}")
                        return False
                else:
                    self.log_result("Video Generation API Endpoint", False, "Invalid response structure")
                    return False
            else:
                self.log_result("Video Generation API Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_result("Video Generation API Endpoint", False, "Request timed out (>180s)")
            return False
        except Exception as e:
            self.log_result("Video Generation API Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_videos_history_endpoint(self):
        """Test videos history endpoint"""
        try:
            response = requests.get(f"{self.base_url}/videos")
            
            if response.status_code == 200:
                videos = response.json()
                
                if isinstance(videos, list):
                    self.log_result("Videos History Endpoint", True, 
                                  f"Retrieved {len(videos)} video records from history",
                                  {"video_count": len(videos)})
                    return True
                else:
                    self.log_result("Videos History Endpoint", False, "Response is not a list")
                    return False
            else:
                self.log_result("Videos History Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Videos History Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_video_generation_validation(self):
        """Test video generation endpoint validation"""
        try:
            # Test missing script
            payload = {}
            response = requests.post(f"{self.base_url}/generate-video", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                if "Script is required" in data.get('error', ''):
                    self.log_result("Video Generation Validation", True, 
                                  "Properly validates missing script parameter")
                    return True
                else:
                    self.log_result("Video Generation Validation", False, f"Unexpected error message: {data}")
                    return False
            else:
                self.log_result("Video Generation Validation", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Video Generation Validation", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all video generation tests"""
        print("=" * 80)
        print("COMPREHENSIVE AI VIDEO GENERATION BACKEND TESTING")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Test Business Description: {TEST_BUSINESS_DESCRIPTION[:100]}...")
        print("=" * 80)
        print()
        
        # Test sequence
        tests = [
            ("Root API Endpoint", self.test_root_endpoint),
            ("Script Generation for Video", self.test_script_generation),
            ("Video Generation Validation", self.test_video_generation_validation),
            ("Avatar Image Generation", self.test_avatar_image_generation),
            ("Scene-Based Visual Prompt Extraction", self.test_scene_extraction),
            ("Background Image Generation", self.test_background_generation),
            ("Video Generation API Endpoint", self.test_video_generation_endpoint),
            ("Videos History Endpoint", self.test_videos_history_endpoint),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 40)
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
            
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Detailed results
        print("DETAILED RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print("=" * 80)
        return passed == total

if __name__ == "__main__":
    tester = VideoGenerationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED! Video generation backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the detailed results above.")
    
    exit(0 if success else 1)