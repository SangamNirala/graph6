#!/usr/bin/env python3
"""
Backend API Testing for Coqui TTS Integration
Tests the fixed Coqui TTS integration focusing on:
1. Voice Models API Endpoint
2. Voiceover Generation API Endpoint  
3. Error Handling with invalid parameters
4. Python Subprocess Integration
"""

import requests
import json
import time
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Get base URL from environment - use internal localhost for testing
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://b08fb6a0-2723-451c-8ea2-f188bed36c6d.preview.emergentagent.com')
# Use internal localhost for backend testing to avoid ingress issues
API_BASE = "http://localhost:3000/api"
TEST_TIMEOUT = 60

class CoquiTTSBackendTester:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_voice_models_endpoint(self):
        """Test GET /api/voice-models endpoint"""
        print("🎤 Testing Voice Models API Endpoint...")
        
        try:
            response = requests.get(f"{API_BASE}/voice-models", timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if models are returned
                if 'models' in data and isinstance(data['models'], dict):
                    models = data['models']
                    expected_models = ['tacotron2_ljspeech', 'vits_ljspeech', 'tacotron2_ek1', 'glow_tts', 'speedy_speech']
                    
                    # Check if all expected models are present
                    missing_models = [model for model in expected_models if model not in models]
                    if not missing_models:
                        # Check model structure
                        sample_model = models['tacotron2_ljspeech']
                        required_fields = ['description', 'quality', 'speed']
                        has_all_fields = all(field in sample_model for field in required_fields)
                        
                        if has_all_fields:
                            self.log_test(
                                "Voice Models Endpoint - Structure", 
                                True, 
                                f"Found {len(models)} models with proper structure"
                            )
                        else:
                            self.log_test(
                                "Voice Models Endpoint - Structure", 
                                False, 
                                f"Missing required fields in model data: {required_fields}"
                            )
                    else:
                        self.log_test(
                            "Voice Models Endpoint - Models", 
                            False, 
                            f"Missing expected models: {missing_models}"
                        )
                
                # Check if formats are returned
                if 'formats' in data and isinstance(data['formats'], dict):
                    formats = data['formats']
                    expected_formats = ['wav', 'mp3', 'ogg', 'flac']
                    missing_formats = [fmt for fmt in expected_formats if fmt not in formats]
                    
                    if not missing_formats:
                        self.log_test(
                            "Voice Models Endpoint - Formats", 
                            True, 
                            f"Found {len(formats)} audio formats"
                        )
                    else:
                        self.log_test(
                            "Voice Models Endpoint - Formats", 
                            False, 
                            f"Missing expected formats: {missing_formats}"
                        )
                else:
                    self.log_test(
                        "Voice Models Endpoint - Formats", 
                        False, 
                        "No formats data returned"
                    )
                    
                # Overall endpoint test
                self.log_test(
                    "Voice Models Endpoint - Overall", 
                    True, 
                    f"Endpoint working, returned {len(data.get('models', {}))} models and {len(data.get('formats', {}))} formats"
                )
                
            else:
                self.log_test(
                    "Voice Models Endpoint - Overall", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Voice Models Endpoint - Overall", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_voiceover_generation_basic(self):
        """Test basic voiceover generation with default parameters"""
        print("🔊 Testing Basic Voiceover Generation...")
        
        test_text = "Hello, this is a test of the Coqui TTS integration for AI business video generation."
        
        try:
            payload = {
                "text": test_text
            }
            
            response = requests.post(
                f"{API_BASE}/generate-voiceover", 
                json=payload, 
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                # Check response headers for TTS metadata
                headers = response.headers
                tts_headers = {
                    'X-TTS-Model-Used': headers.get('X-TTS-Model-Used'),
                    'X-TTS-Fallback-Used': headers.get('X-TTS-Fallback-Used'),
                    'X-TTS-Format': headers.get('X-TTS-Format'),
                    'X-TTS-Duration': headers.get('X-TTS-Duration')
                }
                
                # Check if we got audio data
                audio_size = len(response.content)
                if audio_size > 1000:  # Reasonable audio file size
                    self.log_test(
                        "Voiceover Generation - Basic", 
                        True, 
                        f"Generated {audio_size} bytes of audio. Headers: {tts_headers}"
                    )
                    
                    # Check if proper headers are present
                    if tts_headers['X-TTS-Model-Used'] and tts_headers['X-TTS-Format']:
                        self.log_test(
                            "Voiceover Generation - TTS Headers", 
                            True, 
                            f"Proper TTS metadata headers present"
                        )
                    else:
                        self.log_test(
                            "Voiceover Generation - TTS Headers", 
                            False, 
                            f"Missing TTS metadata headers: {tts_headers}"
                        )
                else:
                    self.log_test(
                        "Voiceover Generation - Basic", 
                        False, 
                        f"Audio size too small: {audio_size} bytes"
                    )
            else:
                self.log_test(
                    "Voiceover Generation - Basic", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Voiceover Generation - Basic", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_voiceover_generation_with_models(self):
        """Test voiceover generation with different voice models"""
        print("🎭 Testing Voiceover Generation with Different Models...")
        
        test_text = "Testing different voice models for business video generation."
        models_to_test = ['tacotron2_ljspeech', 'vits_ljspeech', 'glow_tts']
        
        for model in models_to_test:
            try:
                payload = {
                    "text": test_text,
                    "voice_model": model
                }
                
                response = requests.post(
                    f"{API_BASE}/generate-voiceover", 
                    json=payload, 
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    audio_size = len(response.content)
                    model_used = response.headers.get('X-TTS-Model-Used')
                    fallback_used = response.headers.get('X-TTS-Fallback-Used')
                    
                    if audio_size > 1000:
                        self.log_test(
                            f"Voiceover Generation - Model {model}", 
                            True, 
                            f"Generated {audio_size} bytes. Model used: {model_used}, Fallback: {fallback_used}"
                        )
                    else:
                        self.log_test(
                            f"Voiceover Generation - Model {model}", 
                            False, 
                            f"Audio size too small: {audio_size} bytes"
                        )
                else:
                    self.log_test(
                        f"Voiceover Generation - Model {model}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text[:200]}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"Voiceover Generation - Model {model}", 
                    False, 
                    f"Request failed: {str(e)}"
                )

    def test_voiceover_generation_with_formats(self):
        """Test voiceover generation with different audio formats"""
        print("🎵 Testing Voiceover Generation with Different Formats...")
        
        test_text = "Testing different audio formats for voiceover generation."
        formats_to_test = ['wav', 'mp3', 'ogg']
        
        for audio_format in formats_to_test:
            try:
                payload = {
                    "text": test_text,
                    "audio_format": audio_format
                }
                
                response = requests.post(
                    f"{API_BASE}/generate-voiceover", 
                    json=payload, 
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    audio_size = len(response.content)
                    format_used = response.headers.get('X-TTS-Format')
                    content_type = response.headers.get('Content-Type')
                    
                    if audio_size > 1000:
                        self.log_test(
                            f"Voiceover Generation - Format {audio_format.upper()}", 
                            True, 
                            f"Generated {audio_size} bytes. Format: {format_used}, Content-Type: {content_type}"
                        )
                    else:
                        self.log_test(
                            f"Voiceover Generation - Format {audio_format.upper()}", 
                            False, 
                            f"Audio size too small: {audio_size} bytes"
                        )
                else:
                    self.log_test(
                        f"Voiceover Generation - Format {audio_format.upper()}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text[:200]}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"Voiceover Generation - Format {audio_format.upper()}", 
                    False, 
                    f"Request failed: {str(e)}"
                )

    def test_error_handling(self):
        """Test error handling with invalid parameters"""
        print("⚠️ Testing Error Handling...")
        
        # Test empty text
        try:
            payload = {"text": ""}
            response = requests.post(f"{API_BASE}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 400:
                self.log_test(
                    "Error Handling - Empty Text", 
                    True, 
                    "Properly rejected empty text with 400 status"
                )
            else:
                self.log_test(
                    "Error Handling - Empty Text", 
                    False, 
                    f"Expected 400, got {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Error Handling - Empty Text", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test missing text parameter
        try:
            payload = {"voice_model": "tacotron2_ljspeech"}
            response = requests.post(f"{API_BASE}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 400:
                self.log_test(
                    "Error Handling - Missing Text", 
                    True, 
                    "Properly rejected missing text parameter with 400 status"
                )
            else:
                self.log_test(
                    "Error Handling - Missing Text", 
                    False, 
                    f"Expected 400, got {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Error Handling - Missing Text", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test invalid voice model (should fallback gracefully)
        try:
            payload = {
                "text": "Testing invalid voice model fallback",
                "voice_model": "invalid_model_name"
            }
            response = requests.post(f"{API_BASE}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                model_used = response.headers.get('X-TTS-Model-Used')
                self.log_test(
                    "Error Handling - Invalid Model", 
                    True, 
                    f"Gracefully handled invalid model, used: {model_used}"
                )
            else:
                self.log_test(
                    "Error Handling - Invalid Model", 
                    False, 
                    f"Should fallback gracefully, got {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Error Handling - Invalid Model", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_python_subprocess_integration(self):
        """Test that Python subprocess calls work correctly"""
        print("🐍 Testing Python Subprocess Integration...")
        
        # This is tested indirectly through the voiceover generation
        # We'll test with a longer text to ensure subprocess doesn't timeout
        long_text = """
        Welcome to our revolutionary AI-powered business solution that transforms the way companies 
        operate in the digital age. Our cutting-edge technology leverages machine learning algorithms 
        to provide unprecedented insights into customer behavior, market trends, and operational efficiency. 
        With our comprehensive suite of tools, businesses can automate complex processes, reduce costs, 
        and increase productivity by up to 300 percent. Join thousands of satisfied customers who have 
        already experienced the transformative power of our platform.
        """
        
        try:
            payload = {
                "text": long_text.strip(),
                "voice_model": "tacotron2_ljspeech",
                "audio_format": "wav"
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/generate-voiceover", json=payload, timeout=120)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                audio_size = len(response.content)
                model_used = response.headers.get('X-TTS-Model-Used')
                fallback_used = response.headers.get('X-TTS-Fallback-Used')
                
                if audio_size > 5000:  # Expect larger audio for longer text
                    self.log_test(
                        "Python Subprocess Integration", 
                        True, 
                        f"Processed long text ({len(long_text)} chars) in {processing_time:.2f}s. "
                        f"Generated {audio_size} bytes. Model: {model_used}, Fallback: {fallback_used}"
                    )
                else:
                    self.log_test(
                        "Python Subprocess Integration", 
                        False, 
                        f"Audio size too small for long text: {audio_size} bytes"
                    )
            else:
                self.log_test(
                    "Python Subprocess Integration", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Python Subprocess Integration", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_fallback_behavior(self):
        """Test fallback behavior when TTS fails"""
        print("🔄 Testing Fallback Behavior...")
        
        # Test with a very long text that might cause TTS to fail
        very_long_text = "Testing fallback behavior. " * 100  # Very long text
        
        try:
            payload = {
                "text": very_long_text,
                "voice_model": "tacotron2_ljspeech"
            }
            
            response = requests.post(f"{API_BASE}/generate-voiceover", json=payload, timeout=120)
            
            if response.status_code == 200:
                audio_size = len(response.content)
                fallback_used = response.headers.get('X-TTS-Fallback-Used')
                model_used = response.headers.get('X-TTS-Model-Used')
                
                # Should still generate audio even if TTS fails
                if audio_size > 1000:
                    self.log_test(
                        "Fallback Behavior", 
                        True, 
                        f"Generated {audio_size} bytes with fallback: {fallback_used}, model: {model_used}"
                    )
                else:
                    self.log_test(
                        "Fallback Behavior", 
                        False, 
                        f"Audio size too small: {audio_size} bytes"
                    )
            else:
                self.log_test(
                    "Fallback Behavior", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Fallback Behavior", 
                False, 
                f"Request failed: {str(e)}"
            )

    def run_all_tests(self):
        """Run all Coqui TTS integration tests"""
        print("🚀 Starting Coqui TTS Integration Backend Tests")
        print(f"API Base URL: {API_BASE}")
        print("=" * 60)
        
        # Run all tests
        self.test_voice_models_endpoint()
        self.test_voiceover_generation_basic()
        self.test_voiceover_generation_with_models()
        self.test_voiceover_generation_with_formats()
        self.test_error_handling()
        self.test_python_subprocess_integration()
        self.test_fallback_behavior()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = CoquiTTSBackendTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)