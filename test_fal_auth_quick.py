#!/usr/bin/env python3
"""
Quick test to verify FAL_KEY authentication without waiting for full video generation
"""
import requests
import json

def test_fal_authentication():
    """Test FAL authentication by checking if requests are accepted"""
    base_url = "https://videofusion-5.preview.emergentagent.com/api"
    test_image_url = "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400"
    
    print("🔑 Quick FAL Authentication Test")
    print("=" * 50)
    
    # Test cost estimation first (should work without FAL call)
    print("1. Testing cost estimation...")
    cost_data = {
        "model": "sora2",
        "mode": "premium",
        "duration": 5,
        "with_audio": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/video/estimate-cost",
            json=cost_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Cost estimation works: ${result.get('estimated_cost', 0):.2f}")
        else:
            print(f"   ❌ Cost estimation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cost estimation error: {str(e)}")
    
    # Test video generation request (will show if auth works)
    print("\n2. Testing video generation request (auth check)...")
    video_data = {
        "image_url": test_image_url,
        "model": "sora2",
        "mode": "premium", 
        "prompt": "Quick test",
        "duration": 5
    }
    
    try:
        # Use a shorter timeout to see if we get immediate auth errors
        response = requests.post(
            f"{base_url}/video/generate",
            json=video_data,
            headers={'Content-Type': 'application/json'},
            timeout=15  # Short timeout to catch immediate errors
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Video generation request ACCEPTED!")
                print(f"      Video ID: {result.get('video_id')}")
                print("      (Generation may still be in progress)")
            else:
                print("   ❌ Video generation request REJECTED!")
                print(f"      Error: {result}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"      Details: {error_detail}")
                
                # Check for specific authentication errors
                error_str = str(error_detail)
                if 'No user found' in error_str:
                    print("      🚨 FAL_KEY AUTHENTICATION FAILED")
                elif 'content_policy' in error_str:
                    print("      ⚠️ Content policy issue (but auth worked)")
                elif 'rate limit' in error_str.lower():
                    print("      ⚠️ Rate limit (but auth worked)")
                    
            except:
                print(f"      Response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("   ⏳ Request timed out (likely processing - auth probably worked)")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_fal_authentication()