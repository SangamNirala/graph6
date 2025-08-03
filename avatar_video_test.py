#!/usr/bin/env python3
"""
Focused Avatar Video Generation Test
"""

import requests
import json
import time

BACKEND_URL = "https://de22dc7e-c52e-4c5b-9703-037e2acf8b06.preview.emergentagent.com/api"

def test_avatar_video_generation():
    """Test the avatar video generation functionality"""
    session = requests.Session()
    
    print("🎬 Testing Avatar Video Generation")
    print("=" * 50)
    
    # Step 1: Generate audio first
    print("Step 1: Generating audio...")
    audio_payload = {
        "text": "Hello! This is a test of the avatar video generation system.",
        "voice_name": "en-US-AriaNeural"
    }
    
    audio_response = session.post(
        f"{BACKEND_URL}/generate-audio",
        json=audio_payload,
        timeout=30
    )
    
    if audio_response.status_code != 200:
        print(f"❌ Audio generation failed: {audio_response.status_code}")
        print(f"Response: {audio_response.text}")
        return False
    
    audio_data = audio_response.json()
    audio_base64 = audio_data["audio_base64"]
    print(f"✅ Audio generated: {len(audio_base64)} chars")
    
    # Step 2: Generate avatar video
    print("Step 2: Generating avatar video...")
    avatar_payload = {
        "audio_base64": audio_base64
    }
    
    avatar_response = session.post(
        f"{BACKEND_URL}/generate-avatar-video",
        json=avatar_payload,
        timeout=120
    )
    
    if avatar_response.status_code != 200:
        print(f"❌ Avatar video generation failed: {avatar_response.status_code}")
        print(f"Response: {avatar_response.text}")
        return False
    
    avatar_data = avatar_response.json()
    video_base64 = avatar_data["video_base64"]
    duration = avatar_data["duration_seconds"]
    request_id = avatar_data["request_id"]
    
    print(f"✅ Avatar video generated:")
    print(f"   - Video size: {len(video_base64)} chars")
    print(f"   - Duration: {duration:.2f} seconds")
    print(f"   - Request ID: {request_id}")
    
    # Step 3: Test error handling
    print("Step 3: Testing error handling...")
    
    # Test empty audio
    empty_response = session.post(
        f"{BACKEND_URL}/generate-avatar-video",
        json={"audio_base64": ""},
        timeout=30
    )
    
    if empty_response.status_code == 400:
        print("✅ Empty audio properly handled")
    else:
        print(f"❌ Empty audio handling failed: {empty_response.status_code}")
    
    # Test invalid base64
    invalid_response = session.post(
        f"{BACKEND_URL}/generate-avatar-video",
        json={"audio_base64": "invalid-base64"},
        timeout=30
    )
    
    if invalid_response.status_code in [400, 500]:
        print("✅ Invalid base64 properly handled")
    else:
        print(f"❌ Invalid base64 handling failed: {invalid_response.status_code}")
    
    print("\n🎉 Avatar video generation test completed!")
    return True

if __name__ == "__main__":
    test_avatar_video_generation()