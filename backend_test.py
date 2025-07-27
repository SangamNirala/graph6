#!/usr/bin/env python3
"""
Backend Testing Suite for AI Business Video Script & Voiceover Generator
Focus: Coqui TTS Integration Testing

Tests the newly implemented Coqui TTS integration including:
1. Coqui TTS Integration Module functionality
2. Enhanced Voiceover Generation API with TTS
3. Voice Models API endpoint
4. Enhanced Mock Audio Fallback
5. Backward compatibility verification
"""

import requests
import json
import sys
import os
import time
import base64
from typing import Dict, Any, List
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:3000/api"
TEST_TIMEOUT = 30

class CoquiTTSBackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASSED"
        else:
            self.failed_tests += 1
            status = "❌ FAILED"
            
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"  Details: {details}")
        if error:
            print(f"  Error: {error}")
        print()

    def test_coqui_tts_module_direct(self):
        """Test 1: Direct Coqui TTS Integration Module Testing"""
        print("🔧 Testing Coqui TTS Integration Module (Direct Python Import)...")
        
        try:
            # Add lib directory to Python path
            sys.path.append('/app/lib')
            from coqui_tts import CoquiTTSGenerator, generate_coqui_voice
            
            # Test 1.1: Module initialization
            try:
                generator = CoquiTTSGenerator()
                self.log_result(
                    "Coqui TTS Module - Initialization", 
                    True, 
                    "CoquiTTSGenerator initialized successfully"
                )
            except Exception as e:
                self.log_result(
                    "Coqui TTS Module - Initialization", 
                    False, 
                    error=str(e)
                )
                return
            
            # Test 1.2: Available models verification
            try:
                models = generator.get_available_models()
                expected_models = ['tacotron2_ljspeech', 'vits_ljspeech', 'tacotron2_ek1', 'glow_tts', 'speedy_speech']
                
                if all(model in models for model in expected_models):
                    self.log_result(
                        "Coqui TTS Module - Voice Models Available", 
                        True, 
                        f"All 5 expected models found: {list(models.keys())}"
                    )
                else:
                    self.log_result(
                        "Coqui TTS Module - Voice Models Available", 
                        False, 
                        f"Missing models. Found: {list(models.keys())}, Expected: {expected_models}"
                    )
            except Exception as e:
                self.log_result(
                    "Coqui TTS Module - Voice Models Available", 
                    False, 
                    error=str(e)
                )
            
            # Test 1.3: Audio formats verification
            try:
                formats = generator.get_supported_formats()
                expected_formats = ['wav', 'mp3', 'ogg', 'flac']
                
                if all(fmt in formats for fmt in expected_formats):
                    self.log_result(
                        "Coqui TTS Module - Audio Formats Available", 
                        True, 
                        f"All 4 expected formats found: {list(formats.keys())}"
                    )
                else:
                    self.log_result(
                        "Coqui TTS Module - Audio Formats Available", 
                        False, 
                        f"Missing formats. Found: {list(formats.keys())}, Expected: {expected_formats}"
                    )
            except Exception as e:
                self.log_result(
                    "Coqui TTS Module - Audio Formats Available", 
                    False, 
                    error=str(e)
                )
            
            # Test 1.4: TTS Generation with default model
            try:
                test_text = "Hello, this is a test of the Coqui TTS integration for business video generation."
                result = generate_coqui_voice(test_text)
                
                if result['success'] and result['audio_data'] and len(result['audio_data']) > 1000:
                    self.log_result(
                        "Coqui TTS Module - Default Voice Generation", 
                        True, 
                        f"Generated {len(result['audio_data'])} bytes audio, Model: {result['model_used']}, Fallback: {result['fallback_used']}"
                    )
                else:
                    self.log_result(
                        "Coqui TTS Module - Default Voice Generation", 
                        False, 
                        f"Generation failed or insufficient data. Success: {result.get('success')}, Data size: {len(result.get('audio_data', []))}"
                    )
            except Exception as e:
                self.log_result(
                    "Coqui TTS Module - Default Voice Generation", 
                    False, 
                    error=str(e)
                )
            
            # Test 1.5: Test different voice models
            test_models = ['tacotron2_ljspeech', 'vits_ljspeech', 'glow_tts']
            for model in test_models:
                try:
                    result = generate_coqui_voice("Testing voice model generation.", model)
                    if result['success'] and result['audio_data']:
                        self.log_result(
                            f"Coqui TTS Module - {model} Voice Model", 
                            True, 
                            f"Generated {len(result['audio_data'])} bytes, Fallback: {result['fallback_used']}"
                        )
                    else:
                        self.log_result(
                            f"Coqui TTS Module - {model} Voice Model", 
                            False, 
                            f"Generation failed. Success: {result.get('success')}"
                        )
                except Exception as e:
                    self.log_result(
                        f"Coqui TTS Module - {model} Voice Model", 
                        False, 
                        error=str(e)
                    )
            
            # Test 1.6: Test different audio formats
            test_formats = ['wav', 'mp3', 'ogg']
            for fmt in test_formats:
                try:
                    result = generate_coqui_voice("Testing audio format conversion.", 'tacotron2_ljspeech', fmt)
                    if result['success'] and result['audio_data'] and result['format'] == fmt:
                        self.log_result(
                            f"Coqui TTS Module - {fmt.upper()} Format", 
                            True, 
                            f"Generated {len(result['audio_data'])} bytes in {fmt} format"
                        )
                    else:
                        self.log_result(
                            f"Coqui TTS Module - {fmt.upper()} Format", 
                            False, 
                            f"Format conversion failed. Expected: {fmt}, Got: {result.get('format')}"
                        )
                except Exception as e:
                    self.log_result(
                        f"Coqui TTS Module - {fmt.upper()} Format", 
                        False, 
                        error=str(e)
                    )
            
            # Test 1.7: Fallback mechanism
            try:
                # Test with empty text to trigger fallback
                result = generate_coqui_voice("")
                if result.get('error') and 'Empty text' in result['error']:
                    self.log_result(
                        "Coqui TTS Module - Empty Text Handling", 
                        True, 
                        "Properly handles empty text input with appropriate error"
                    )
                else:
                    self.log_result(
                        "Coqui TTS Module - Empty Text Handling", 
                        False, 
                        f"Unexpected response to empty text: {result}"
                    )
            except Exception as e:
                self.log_result(
                    "Coqui TTS Module - Empty Text Handling", 
                    False, 
                    error=str(e)
                )
                
        except ImportError as e:
            self.log_result(
                "Coqui TTS Module - Import", 
                False, 
                error=f"Cannot import Coqui TTS module: {e}"
            )

    def test_voice_models_api_endpoint(self):
        """Test 2: Voice Models API Endpoint"""
        print("🎤 Testing Voice Models API Endpoint...")
        
        try:
            response = requests.get(f"{BASE_URL}/voice-models", timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if models are present
                if 'models' in data and 'formats' in data:
                    models = data['models']
                    formats = data['formats']
                    
                    expected_models = ['tacotron2_ljspeech', 'vits_ljspeech', 'tacotron2_ek1', 'glow_tts', 'speedy_speech']
                    expected_formats = ['wav', 'mp3', 'ogg', 'flac']
                    
                    models_ok = all(model in models for model in expected_models)
                    formats_ok = all(fmt in formats for fmt in expected_formats)
                    
                    if models_ok and formats_ok:
                        self.log_result(
                            "Voice Models API - Endpoint Response", 
                            True, 
                            f"Returned {len(models)} models and {len(formats)} formats"
                        )
                    else:
                        self.log_result(
                            "Voice Models API - Endpoint Response", 
                            False, 
                            f"Missing data. Models OK: {models_ok}, Formats OK: {formats_ok}"
                        )
                else:
                    self.log_result(
                        "Voice Models API - Endpoint Response", 
                        False, 
                        f"Missing 'models' or 'formats' in response: {list(data.keys())}"
                    )
            else:
                self.log_result(
                    "Voice Models API - Endpoint Response", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Voice Models API - Endpoint Response", 
                False, 
                error=str(e)
            )

    def test_enhanced_voiceover_generation_api(self):
        """Test 3: Enhanced Voiceover Generation API"""
        print("🔊 Testing Enhanced Voiceover Generation API...")
        
        test_text = "Welcome to our AI-powered business solution. This innovative platform transforms how companies operate, delivering exceptional results through cutting-edge technology and intelligent automation."
        
        # Test 3.1: Default voiceover generation
        try:
            payload = {"text": test_text}
            response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                # Check TTS metadata headers
                headers = response.headers
                required_headers = ['X-TTS-Model-Used', 'X-TTS-Fallback-Used', 'X-TTS-Format', 'X-TTS-Duration']
                
                headers_present = all(header in headers for header in required_headers)
                audio_size = len(response.content)
                
                if headers_present and audio_size > 1000:
                    self.log_result(
                        "Enhanced Voiceover API - Default Generation", 
                        True, 
                        f"Generated {audio_size} bytes audio with TTS metadata headers. Model: {headers.get('X-TTS-Model-Used')}, Fallback: {headers.get('X-TTS-Fallback-Used')}"
                    )
                else:
                    self.log_result(
                        "Enhanced Voiceover API - Default Generation", 
                        False, 
                        f"Missing headers or insufficient audio. Headers OK: {headers_present}, Audio size: {audio_size}"
                    )
            else:
                self.log_result(
                    "Enhanced Voiceover API - Default Generation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Enhanced Voiceover API - Default Generation", 
                False, 
                error=str(e)
            )
        
        # Test 3.2: Voice model parameter testing
        test_models = ['tacotron2_ljspeech', 'vits_ljspeech', 'glow_tts']
        for model in test_models:
            try:
                payload = {"text": "Testing voice model selection.", "voice_model": model}
                response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
                
                if response.status_code == 200:
                    model_used = response.headers.get('X-TTS-Model-Used', '')
                    audio_size = len(response.content)
                    
                    if audio_size > 500:
                        self.log_result(
                            f"Enhanced Voiceover API - {model} Model", 
                            True, 
                            f"Generated {audio_size} bytes with model: {model_used}"
                        )
                    else:
                        self.log_result(
                            f"Enhanced Voiceover API - {model} Model", 
                            False, 
                            f"Insufficient audio generated: {audio_size} bytes"
                        )
                else:
                    self.log_result(
                        f"Enhanced Voiceover API - {model} Model", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Enhanced Voiceover API - {model} Model", 
                    False, 
                    error=str(e)
                )
        
        # Test 3.3: Audio format parameter testing
        test_formats = ['wav', 'mp3', 'ogg']
        for fmt in test_formats:
            try:
                payload = {"text": "Testing audio format selection.", "audio_format": fmt}
                response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
                
                if response.status_code == 200:
                    format_used = response.headers.get('X-TTS-Format', '')
                    content_type = response.headers.get('Content-Type', '')
                    audio_size = len(response.content)
                    
                    expected_mime = {
                        'wav': 'audio/wav',
                        'mp3': 'audio/mpeg', 
                        'ogg': 'audio/ogg'
                    }
                    
                    if format_used == fmt and expected_mime[fmt] in content_type and audio_size > 500:
                        self.log_result(
                            f"Enhanced Voiceover API - {fmt.upper()} Format", 
                            True, 
                            f"Generated {audio_size} bytes in {fmt} format with correct MIME type"
                        )
                    else:
                        self.log_result(
                            f"Enhanced Voiceover API - {fmt.upper()} Format", 
                            False, 
                            f"Format mismatch. Expected: {fmt}, Got: {format_used}, MIME: {content_type}"
                        )
                else:
                    self.log_result(
                        f"Enhanced Voiceover API - {fmt.upper()} Format", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Enhanced Voiceover API - {fmt.upper()} Format", 
                    False, 
                    error=str(e)
                )
        
        # Test 3.4: Combined parameters
        try:
            payload = {
                "text": "Testing combined voice model and audio format parameters.",
                "voice_model": "vits_ljspeech",
                "audio_format": "mp3"
            }
            response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                model_used = response.headers.get('X-TTS-Model-Used', '')
                format_used = response.headers.get('X-TTS-Format', '')
                content_type = response.headers.get('Content-Type', '')
                audio_size = len(response.content)
                
                if format_used == 'mp3' and 'audio/mpeg' in content_type and audio_size > 500:
                    self.log_result(
                        "Enhanced Voiceover API - Combined Parameters", 
                        True, 
                        f"Generated {audio_size} bytes with model: {model_used}, format: {format_used}"
                    )
                else:
                    self.log_result(
                        "Enhanced Voiceover API - Combined Parameters", 
                        False, 
                        f"Parameter combination failed. Model: {model_used}, Format: {format_used}, Size: {audio_size}"
                    )
            else:
                self.log_result(
                    "Enhanced Voiceover API - Combined Parameters", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Enhanced Voiceover API - Combined Parameters", 
                False, 
                error=str(e)
            )

    def test_enhanced_mock_audio_fallback(self):
        """Test 4: Enhanced Mock Audio Fallback"""
        print("🎵 Testing Enhanced Mock Audio Fallback...")
        
        # Test with various text lengths to verify duration estimation
        test_cases = [
            ("Short text.", 3),  # Should be minimum 3 seconds
            ("This is a medium length text that should generate audio with appropriate duration based on word count estimation.", 15),
            ("Very long text " * 50, 30)  # Should be capped at 30 seconds
        ]
        
        for i, (text, expected_min_duration) in enumerate(test_cases):
            try:
                payload = {"text": text}
                response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
                
                if response.status_code == 200:
                    duration = float(response.headers.get('X-TTS-Duration', '0'))
                    audio_size = len(response.content)
                    fallback_used = response.headers.get('X-TTS-Fallback-Used', 'false')
                    
                    # Check if duration estimation is reasonable
                    duration_ok = duration >= 3 and duration <= 30
                    size_ok = audio_size > 1000  # Should have substantial audio data
                    
                    if duration_ok and size_ok:
                        self.log_result(
                            f"Enhanced Mock Audio - Text Length Test {i+1}", 
                            True, 
                            f"Generated {audio_size} bytes, Duration: {duration}s, Fallback: {fallback_used}"
                        )
                    else:
                        self.log_result(
                            f"Enhanced Mock Audio - Text Length Test {i+1}", 
                            False, 
                            f"Duration or size issue. Duration: {duration}s (OK: {duration_ok}), Size: {audio_size} (OK: {size_ok})"
                        )
                else:
                    self.log_result(
                        f"Enhanced Mock Audio - Text Length Test {i+1}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Enhanced Mock Audio - Text Length Test {i+1}", 
                    False, 
                    error=str(e)
                )

    def test_mongodb_storage_integration(self):
        """Test 5: MongoDB Storage with TTS Metadata"""
        print("💾 Testing MongoDB Storage Integration...")
        
        try:
            # Generate a voiceover to create a database record
            payload = {
                "text": "Testing MongoDB storage with TTS metadata fields.",
                "voice_model": "tacotron2_ljspeech",
                "audio_format": "wav"
            }
            response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                # Wait a moment for database write
                time.sleep(1)
                
                # Check voiceovers history
                history_response = requests.get(f"{BASE_URL}/voiceovers", timeout=TEST_TIMEOUT)
                
                if history_response.status_code == 200:
                    voiceovers = history_response.json()
                    
                    if voiceovers and len(voiceovers) > 0:
                        latest = voiceovers[0]  # Most recent
                        
                        # Check for TTS metadata fields
                        required_fields = ['voice_model', 'audio_format', 'fallback_used', 'model_used', 'duration_estimate']
                        fields_present = all(field in latest for field in required_fields)
                        
                        if fields_present:
                            self.log_result(
                                "MongoDB Storage - TTS Metadata Fields", 
                                True, 
                                f"All TTS metadata fields present: {[f for f in required_fields if f in latest]}"
                            )
                        else:
                            missing_fields = [f for f in required_fields if f not in latest]
                            self.log_result(
                                "MongoDB Storage - TTS Metadata Fields", 
                                False, 
                                f"Missing TTS metadata fields: {missing_fields}"
                            )
                    else:
                        self.log_result(
                            "MongoDB Storage - TTS Metadata Fields", 
                            False, 
                            "No voiceover records found in database"
                        )
                else:
                    self.log_result(
                        "MongoDB Storage - TTS Metadata Fields", 
                        False, 
                        f"Failed to retrieve voiceovers history: HTTP {history_response.status_code}"
                    )
            else:
                self.log_result(
                    "MongoDB Storage - TTS Metadata Fields", 
                    False, 
                    f"Failed to generate voiceover for storage test: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "MongoDB Storage - TTS Metadata Fields", 
                False, 
                error=str(e)
            )

    def test_backward_compatibility(self):
        """Test 6: Backward Compatibility"""
        print("🔄 Testing Backward Compatibility...")
        
        # Test 6.1: Script generation still works
        try:
            payload = {"prompt": "AI-powered customer relationship management software for small businesses"}
            response = requests.post(f"{BASE_URL}/generate-script", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if 'script' in data and len(data['script']) > 100:
                    self.log_result(
                        "Backward Compatibility - Script Generation", 
                        True, 
                        f"Generated {len(data['script'])} character script"
                    )
                else:
                    self.log_result(
                        "Backward Compatibility - Script Generation", 
                        False, 
                        f"Script generation returned insufficient content: {len(data.get('script', ''))}"
                    )
            else:
                self.log_result(
                    "Backward Compatibility - Script Generation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Backward Compatibility - Script Generation", 
                False, 
                error=str(e)
            )
        
        # Test 6.2: Basic voiceover generation without new parameters
        try:
            payload = {"text": "Testing backward compatibility for voiceover generation."}
            response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                audio_size = len(response.content)
                if audio_size > 500:
                    self.log_result(
                        "Backward Compatibility - Basic Voiceover", 
                        True, 
                        f"Generated {audio_size} bytes audio without new parameters"
                    )
                else:
                    self.log_result(
                        "Backward Compatibility - Basic Voiceover", 
                        False, 
                        f"Insufficient audio generated: {audio_size} bytes"
                    )
            else:
                self.log_result(
                    "Backward Compatibility - Basic Voiceover", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Backward Compatibility - Basic Voiceover", 
                False, 
                error=str(e)
            )
        
        # Test 6.3: History endpoints still work
        try:
            scripts_response = requests.get(f"{BASE_URL}/scripts", timeout=TEST_TIMEOUT)
            voiceovers_response = requests.get(f"{BASE_URL}/voiceovers", timeout=TEST_TIMEOUT)
            
            scripts_ok = scripts_response.status_code == 200
            voiceovers_ok = voiceovers_response.status_code == 200
            
            if scripts_ok and voiceovers_ok:
                self.log_result(
                    "Backward Compatibility - History Endpoints", 
                    True, 
                    "Both scripts and voiceovers history endpoints working"
                )
            else:
                self.log_result(
                    "Backward Compatibility - History Endpoints", 
                    False, 
                    f"Scripts OK: {scripts_ok}, Voiceovers OK: {voiceovers_ok}"
                )
                
        except Exception as e:
            self.log_result(
                "Backward Compatibility - History Endpoints", 
                False, 
                error=str(e)
            )

    def test_error_handling(self):
        """Test 7: Error Handling for Invalid Parameters"""
        print("⚠️ Testing Error Handling...")
        
        # Test 7.1: Invalid voice model
        try:
            payload = {"text": "Testing invalid voice model.", "voice_model": "invalid_model"}
            response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            # Should still work with fallback to default model
            if response.status_code == 200:
                model_used = response.headers.get('X-TTS-Model-Used', '')
                if model_used in ['tacotron2_ljspeech', 'mock_audio']:
                    self.log_result(
                        "Error Handling - Invalid Voice Model", 
                        True, 
                        f"Gracefully handled invalid model, used: {model_used}"
                    )
                else:
                    self.log_result(
                        "Error Handling - Invalid Voice Model", 
                        False, 
                        f"Unexpected model used: {model_used}"
                    )
            else:
                self.log_result(
                    "Error Handling - Invalid Voice Model", 
                    False, 
                    f"Should handle invalid model gracefully: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Error Handling - Invalid Voice Model", 
                False, 
                error=str(e)
            )
        
        # Test 7.2: Invalid audio format
        try:
            payload = {"text": "Testing invalid audio format.", "audio_format": "invalid_format"}
            response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            # Should still work with fallback to default format
            if response.status_code == 200:
                format_used = response.headers.get('X-TTS-Format', '')
                if format_used == 'wav':
                    self.log_result(
                        "Error Handling - Invalid Audio Format", 
                        True, 
                        f"Gracefully handled invalid format, used: {format_used}"
                    )
                else:
                    self.log_result(
                        "Error Handling - Invalid Audio Format", 
                        False, 
                        f"Unexpected format used: {format_used}"
                    )
            else:
                self.log_result(
                    "Error Handling - Invalid Audio Format", 
                    False, 
                    f"Should handle invalid format gracefully: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Error Handling - Invalid Audio Format", 
                False, 
                error=str(e)
            )
        
        # Test 7.3: Empty text handling
        try:
            payload = {"text": ""}
            response = requests.post(f"{BASE_URL}/generate-voiceover", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 400:
                self.log_result(
                    "Error Handling - Empty Text", 
                    True, 
                    "Properly returns 400 error for empty text"
                )
            else:
                self.log_result(
                    "Error Handling - Empty Text", 
                    False, 
                    f"Should return 400 for empty text: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Error Handling - Empty Text", 
                False, 
                error=str(e)
            )

    def run_all_tests(self):
        """Run all backend tests for Coqui TTS integration"""
        print("🚀 Starting Comprehensive Coqui TTS Backend Testing...")
        print("=" * 80)
        
        # Run all test suites
        self.test_coqui_tts_module_direct()
        self.test_voice_models_api_endpoint()
        self.test_enhanced_voiceover_generation_api()
        self.test_enhanced_mock_audio_fallback()
        self.test_mongodb_storage_integration()
        self.test_backward_compatibility()
        self.test_error_handling()
        
        # Print summary
        print("=" * 80)
        print("🏁 COQUI TTS BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Print failed tests details
        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}")
                    if result['error']:
                        print(f"    Error: {result['error']}")
            print()
        
        # Overall assessment
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Coqui TTS integration is working perfectly.")
        elif self.failed_tests <= 3:
            print("⚠️ MOSTLY WORKING: Minor issues detected but core functionality intact.")
        else:
            print("🚨 CRITICAL ISSUES: Multiple test failures indicate significant problems.")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    print("🔧 AI Business Video Script & Voiceover Generator - Coqui TTS Backend Testing")
    print("Testing internal API at:", BASE_URL)
    print()
    
    tester = CoquiTTSBackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)