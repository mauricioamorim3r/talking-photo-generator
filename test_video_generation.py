#!/usr/bin/env python3
"""
Test video generation with Sora 2 and Veo 3 using the updated FAL_KEY
"""
import requests
import json
import time

def test_video_generation():
    """Test both Sora 2 and Veo 3 video generation"""
    base_url = "https://videofusion-5.preview.emergentagent.com/api"
    test_image_url = "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400"
    
    print("🎬 Testing Video Generation with Updated FAL_KEY")
    print("=" * 60)
    print(f"Test Image: {test_image_url}")
    print()
    
    # Test Sora 2
    print("🔍 Testing Sora 2 Video Generation...")
    sora2_data = {
        "image_url": test_image_url,
        "model": "sora2",
        "mode": "premium",
        "prompt": "Cat looking up with curiosity, ears moving, eyes focused. Medium shot, natural lighting.",
        "duration": 5
    }
    
    try:
        response = requests.post(
            f"{base_url}/video/generate",
            json=sora2_data,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Sora 2 Generation SUCCESSFUL!")
                print(f"   Video URL: {result.get('video_url')}")
                print(f"   Cost: ${result.get('cost', 0):.2f}")
                print(f"   Video ID: {result.get('video_id')}")
            else:
                print("❌ Sora 2 Generation FAILED!")
                print(f"   Error: {result}")
        else:
            print(f"❌ Sora 2 HTTP Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Details: {error_detail}")
            except:
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Sora 2 Exception: {str(e)}")
    
    print()
    
    # Test Veo 3
    print("🔍 Testing Veo 3 Video Generation...")
    veo3_data = {
        "image_url": test_image_url,
        "model": "veo3", 
        "mode": "premium",
        "prompt": "Cat turning head slowly, cinematic close-up, soft lighting.",
        "duration": 5  # Backend will convert this to "8s" for Veo 3
    }
    
    try:
        response = requests.post(
            f"{base_url}/video/generate",
            json=veo3_data,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Veo 3 Generation SUCCESSFUL!")
                print(f"   Video URL: {result.get('video_url')}")
                print(f"   Cost: ${result.get('cost', 0):.2f}")
                print(f"   Video ID: {result.get('video_id')}")
            else:
                print("❌ Veo 3 Generation FAILED!")
                print(f"   Error: {result}")
        else:
            print(f"❌ Veo 3 HTTP Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Details: {error_detail}")
                
                # Check for specific error types
                if 'content_policy_violation' in str(error_detail):
                    print("   🚨 Content Policy Violation detected")
                elif 'No user found' in str(error_detail):
                    print("   🚨 Authentication Error - FAL_KEY issue")
                    
            except:
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Veo 3 Exception: {str(e)}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_video_generation()