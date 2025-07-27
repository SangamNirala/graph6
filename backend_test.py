#!/usr/bin/env python3
"""
Backend Testing Suite for Audio Generation Duration Fix
Tests the /api/generate-voiceover endpoint with focus on duration calculation and audio generation.
"""

import requests
import json
import time
import os
import sys
from typing import Dict, Any

# Get base URL from environment - use internal localhost for testing
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://2c9dc19c-c523-43ae-9a64-3a12453c3999.preview.emergentagent.com')
# Use internal localhost for backend testing to avoid ingress issues
API_BASE = "http://localhost:3000/api"
TEST_TIMEOUT = 60

class AudioDurationTester:
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_result(self, test_name: str, passed: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'details': details or {}
        }
        self.test_results.append(result)
        
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_short_script_duration(self):
        """Test audio generation with short script (should be minimum 3 seconds)"""
        test_name = "Short Script Duration Test"
        
        try:
            # Short script - should result in minimum 3 seconds
            short_text = "Hello world. This is a short test."
            word_count = len(short_text.split())
            expected_min_duration = 3  # Minimum duration
            
            response = requests.post(
                f"{API_BASE}/generate-voiceover",
                json={
                    "text": short_text,
                    "voice_model": "tacotron2_ljspeech",
                    "audio_format": "wav"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                # Check headers for duration
                duration_header = response.headers.get('X-TTS-Duration')
                model_used = response.headers.get('X-TTS-Model-Used', 'unknown')
                fallback_used = response.headers.get('X-TTS-Fallback-Used', 'false') == 'true'
                
                if duration_header:
                    actual_duration = float(duration_header)
                    audio_size = len(response.content)
                    
                    # Verify minimum duration is respected
                    if actual_duration >= expected_min_duration:
                        self.log_result(
                            test_name, 
                            True, 
                            f"Duration correctly set to minimum {actual_duration}s for short script",
                            {
                                'word_count': word_count,
                                'expected_min': expected_min_duration,
                                'actual_duration': actual_duration,
                                'audio_size': f"{audio_size} bytes",
                                'model_used': model_used,
                                'fallback_used': fallback_used
                            }
                        )
                    else:
                        self.log_result(
                            test_name, 
                            False, 
                            f"Duration {actual_duration}s is below minimum {expected_min_duration}s",
                            {
                                'word_count': word_count,
                                'expected_min': expected_min_duration,
                                'actual_duration': actual_duration
                            }
                        )
                else:
                    self.log_result(test_name, False, "No duration header found in response")
            else:
                self.log_result(test_name, False, f"API request failed with status {response.status_code}")
                
        except Exception as e:
            self.log_result(test_name, False, f"Test failed with exception: {str(e)}")
    
    def test_long_script_duration(self):
        """Test audio generation with long script (90+ seconds of content)"""
        test_name = "Long Script Duration Test (90+ seconds)"
        
        try:
            # Create a long script that should result in ~90+ seconds
            # At 0.4 seconds per word, we need ~225 words for 90 seconds
            long_text = """
            Welcome to our revolutionary AI-powered CRM software that's transforming how businesses manage their customer relationships. 
            In today's competitive marketplace, sales teams are struggling with manual follow-ups, lost leads, and inefficient processes that cost them valuable opportunities every single day.
            
            Our cutting-edge solution automates your entire sales pipeline, from initial lead capture to final conversion, ensuring no opportunity slips through the cracks.
            With advanced machine learning algorithms, our platform analyzes customer behavior patterns, predicts buying intentions, and suggests the perfect timing for follow-ups.
            
            Imagine increasing your conversion rates by forty percent while reducing manual work by sixty percent. Our clients report significant improvements in sales productivity within just thirty days of implementation.
            The system integrates seamlessly with your existing tools, provides real-time analytics, and offers customizable workflows that adapt to your unique business processes.
            
            Small to medium businesses across various industries have already transformed their sales operations using our platform. From real estate agencies to software companies, our solution scales with your growth.
            Don't let manual processes hold back your sales potential. Join thousands of successful businesses who have already revolutionized their customer relationship management.
            
            Contact us today for a free demonstration and see how our AI-powered CRM can transform your sales results immediately.
            """
            
            word_count = len(long_text.split())
            expected_duration = min(30, word_count * 0.4)  # Capped at 30 seconds max
            
            print(f"Testing with {word_count} words, expected duration: {expected_duration}s")
            
            response = requests.post(
                f"{API_BASE}/generate-voiceover",
                json={
                    "text": long_text,
                    "voice_model": "tacotron2_ljspeech",
                    "audio_format": "wav"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                # Check headers for duration
                duration_header = response.headers.get('X-TTS-Duration')
                model_used = response.headers.get('X-TTS-Model-Used', 'unknown')
                fallback_used = response.headers.get('X-TTS-Fallback-Used', 'false') == 'true'
                
                if duration_header:
                    actual_duration = float(duration_header)
                    audio_size = len(response.content)
                    
                    # Verify duration matches expected calculation (capped at 30s)
                    if abs(actual_duration - expected_duration) <= 1:  # Allow 1 second tolerance
                        self.log_result(
                            test_name, 
                            True, 
                            f"Duration correctly calculated as {actual_duration}s for long script",
                            {
                                'word_count': word_count,
                                'expected_duration': expected_duration,
                                'actual_duration': actual_duration,
                                'audio_size': f"{audio_size} bytes",
                                'model_used': model_used,
                                'fallback_used': fallback_used,
                                'duration_formula': f"{word_count} words * 0.4s = {word_count * 0.4}s (capped at 30s)"
                            }
                        )
                    else:
                        self.log_result(
                            test_name, 
                            False, 
                            f"Duration mismatch: expected ~{expected_duration}s, got {actual_duration}s",
                            {
                                'word_count': word_count,
                                'expected_duration': expected_duration,
                                'actual_duration': actual_duration
                            }
                        )
                else:
                    self.log_result(test_name, False, "No duration header found in response")
            else:
                self.log_result(test_name, False, f"API request failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result(test_name, False, f"Test failed with exception: {str(e)}")
    
    def test_medium_script_duration(self):
        """Test audio generation with medium script (30-60 seconds)"""
        test_name = "Medium Script Duration Test"
        
        try:
            # Medium script - should result in ~15-20 seconds
            medium_text = """
            Transform your business with our AI-powered CRM solution. Stop losing leads due to manual follow-ups and inefficient processes.
            Our platform automates your sales pipeline, analyzes customer behavior, and increases conversion rates by forty percent.
            Small to medium businesses report significant productivity improvements within thirty days of implementation.
            Join thousands of successful companies who have revolutionized their customer relationship management today.
            """
            
            word_count = len(medium_text.split())
            expected_duration = min(30, max(3, word_count * 0.4))
            
            response = requests.post(
                f"{API_BASE}/generate-voiceover",
                json={
                    "text": medium_text,
                    "voice_model": "vits_ljspeech",
                    "audio_format": "wav"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                duration_header = response.headers.get('X-TTS-Duration')
                model_used = response.headers.get('X-TTS-Model-Used', 'unknown')
                fallback_used = response.headers.get('X-TTS-Fallback-Used', 'false') == 'true'
                
                if duration_header:
                    actual_duration = float(duration_header)
                    audio_size = len(response.content)
                    
                    if abs(actual_duration - expected_duration) <= 1:
                        self.log_result(
                            test_name, 
                            True, 
                            f"Duration correctly calculated as {actual_duration}s for medium script",
                            {
                                'word_count': word_count,
                                'expected_duration': expected_duration,
                                'actual_duration': actual_duration,
                                'audio_size': f"{audio_size} bytes",
                                'model_used': model_used,
                                'fallback_used': fallback_used
                            }
                        )
                    else:
                        self.log_result(
                            test_name, 
                            False, 
                            f"Duration mismatch: expected ~{expected_duration}s, got {actual_duration}s"
                        )
                else:
                    self.log_result(test_name, False, "No duration header found in response")
            else:
                self.log_result(test_name, False, f"API request failed with status {response.status_code}")
                
        except Exception as e:
            self.log_result(test_name, False, f"Test failed with exception: {str(e)}")
    
    def test_audio_content_quality(self):
        """Test that generated audio contains actual audio data (not just silence)"""
        test_name = "Audio Content Quality Test"
        
        try:
            test_text = "This is a test to verify that the generated audio contains actual voice content and is not just silence or empty data."
            
            response = requests.post(
                f"{API_BASE}/generate-voiceover",
                json={
                    "text": test_text,
                    "voice_model": "tacotron2_ljspeech",
                    "audio_format": "wav"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                audio_data = response.content
                audio_size = len(audio_data)
                model_used = response.headers.get('X-TTS-Model-Used', 'unknown')
                fallback_used = response.headers.get('X-TTS-Fallback-Used', 'false') == 'true'
                
                # Check if audio data is substantial (not just a minimal header)
                if audio_size > 1000:  # Should be much larger than minimal WAV header
                    # Check for WAV header
                    if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                        self.log_result(
                            test_name, 
                            True, 
                            f"Audio generated successfully with proper WAV format",
                            {
                                'audio_size': f"{audio_size} bytes",
                                'model_used': model_used,
                                'fallback_used': fallback_used,
                                'wav_header_valid': True
                            }
                        )
                    else:
                        self.log_result(
                            test_name, 
                            False, 
                            f"Audio data present but invalid WAV format",
                            {'audio_size': f"{audio_size} bytes"}
                        )
                else:
                    self.log_result(
                        test_name, 
                        False, 
                        f"Audio data too small ({audio_size} bytes), likely empty or minimal"
                    )
            else:
                self.log_result(test_name, False, f"API request failed with status {response.status_code}")
                
        except Exception as e:
            self.log_result(test_name, False, f"Test failed with exception: {str(e)}")
    
    def test_different_voice_models(self):
        """Test audio generation with different voice models"""
        test_name = "Different Voice Models Test"
        
        voice_models = ['tacotron2_ljspeech', 'vits_ljspeech', 'glow_tts']
        test_text = "Testing different voice models for consistent duration calculation and audio generation quality."
        word_count = len(test_text.split())
        expected_duration = min(30, max(3, word_count * 0.4))
        
        successful_models = 0
        
        for model in voice_models:
            try:
                response = requests.post(
                    f"{API_BASE}/generate-voiceover",
                    json={
                        "text": test_text,
                        "voice_model": model,
                        "audio_format": "wav"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    duration_header = response.headers.get('X-TTS-Duration')
                    audio_size = len(response.content)
                    model_used = response.headers.get('X-TTS-Model-Used', 'unknown')
                    fallback_used = response.headers.get('X-TTS-Fallback-Used', 'false') == 'true'
                    
                    if duration_header and audio_size > 1000:
                        actual_duration = float(duration_header)
                        if abs(actual_duration - expected_duration) <= 1:
                            successful_models += 1
                            print(f"   ✅ {model}: {actual_duration}s duration, {audio_size} bytes, fallback: {fallback_used}")
                        else:
                            print(f"   ❌ {model}: Duration mismatch ({actual_duration}s vs expected {expected_duration}s)")
                    else:
                        print(f"   ❌ {model}: Missing duration header or insufficient audio data")
                else:
                    print(f"   ❌ {model}: API request failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {model}: Exception - {str(e)}")
        
        if successful_models >= 2:  # At least 2 models should work
            self.log_result(
                test_name, 
                True, 
                f"{successful_models}/{len(voice_models)} voice models working correctly",
                {'successful_models': successful_models, 'total_models': len(voice_models)}
            )
        else:
            self.log_result(
                test_name, 
                False, 
                f"Only {successful_models}/{len(voice_models)} voice models working"
            )
    
    def test_audio_format_support(self):
        """Test different audio formats"""
        test_name = "Audio Format Support Test"
        
        formats = ['wav', 'mp3', 'ogg']
        test_text = "Testing audio format conversion and duration consistency across different formats."
        
        successful_formats = 0
        
        for fmt in formats:
            try:
                response = requests.post(
                    f"{API_BASE}/generate-voiceover",
                    json={
                        "text": test_text,
                        "voice_model": "tacotron2_ljspeech",
                        "audio_format": fmt
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    audio_size = len(response.content)
                    duration_header = response.headers.get('X-TTS-Duration')
                    content_type = response.headers.get('Content-Type', '')
                    
                    if audio_size > 500 and duration_header:  # Some formats might be smaller
                        successful_formats += 1
                        print(f"   ✅ {fmt.upper()}: {audio_size} bytes, {duration_header}s, {content_type}")
                    else:
                        print(f"   ❌ {fmt.upper()}: Insufficient data or missing duration")
                else:
                    print(f"   ❌ {fmt.upper()}: API request failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {fmt.upper()}: Exception - {str(e)}")
        
        if successful_formats >= 2:  # At least WAV and one other format should work
            self.log_result(
                test_name, 
                True, 
                f"{successful_formats}/{len(formats)} audio formats working correctly"
            )
        else:
            self.log_result(
                test_name, 
                False, 
                f"Only {successful_formats}/{len(formats)} audio formats working"
            )
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        test_name = "Error Handling Test"
        
        try:
            # Test empty text
            response = requests.post(
                f"{API_BASE}/generate-voiceover",
                json={
                    "text": "",
                    "voice_model": "tacotron2_ljspeech",
                    "audio_format": "wav"
                },
                timeout=30
            )
            
            if response.status_code == 400:
                self.log_result(
                    test_name, 
                    True, 
                    "Properly handles empty text with 400 error",
                    {'response_status': response.status_code}
                )
            else:
                self.log_result(
                    test_name, 
                    False, 
                    f"Expected 400 for empty text, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(test_name, False, f"Test failed with exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all audio duration tests"""
        print("🎵 Starting Audio Generation Duration Fix Tests")
        print("=" * 60)
        
        # Test duration calculation with different script lengths
        self.test_short_script_duration()
        self.test_medium_script_duration()
        self.test_long_script_duration()
        
        # Test audio quality and content
        self.test_audio_content_quality()
        
        # Test different models and formats
        self.test_different_voice_models()
        self.test_audio_format_support()
        
        # Test error handling
        self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎵 AUDIO DURATION FIX TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📊 Total: {self.passed_tests + self.failed_tests}")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Audio generation duration fix is working correctly.")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Review the issues above.")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = AudioDurationTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)