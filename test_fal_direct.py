#!/usr/bin/env python3
"""
Direct FAL.ai API test to verify the updated key works
"""
import os
import sys
from dotenv import load_dotenv
import fal_client

# Load environment variables
load_dotenv('/app/backend/.env')

def test_fal_key():
    """Test FAL_KEY directly"""
    fal_key = os.environ.get('FAL_KEY', '')
    print(f"Testing FAL_KEY: {fal_key}")
    
    if not fal_key:
        print("❌ FAL_KEY not found in environment")
        return False
    
    # Set the key in environment for fal_client
    os.environ['FAL_KEY'] = fal_key
    
    try:
        print("🔍 Testing Sora 2 model...")
        
        # Test with a simple request to Sora 2
        handler = fal_client.submit(
            "fal-ai/sora-2/image-to-video",
            arguments={
                "image_url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400",
                "prompt": "Cat looking up with curiosity"
            }
        )
        
        print("✅ Request submitted successfully")
        print("⏳ Waiting for result...")
        
        # Get the result
        result = handler.get()
        
        print("✅ Sora 2 test successful!")
        print(f"Result: {result}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ FAL API Error: {error_msg}")
        
        if 'No user found' in error_msg:
            print("🚨 Authentication Error: The FAL_KEY is not valid or not properly formatted")
            print("   - Check if the key format is correct: key_id:secret")
            print("   - Verify the key is active and has credits")
        elif 'rate limit' in error_msg.lower():
            print("⚠️ Rate Limit: Too many requests")
        elif 'insufficient' in error_msg.lower():
            print("💰 Insufficient Credits: Account may be out of credits")
        else:
            print(f"🔍 Other Error: {error_msg}")
        
        return False

def test_veo3():
    """Test Veo 3 model"""
    try:
        print("\n🔍 Testing Veo 3 model...")
        
        handler = fal_client.submit(
            "fal-ai/veo3.1/image-to-video",
            arguments={
                "image_url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400",
                "prompt": "Cat turning head slowly, cinematic close-up",
                "duration": 5
            }
        )
        
        print("✅ Veo 3 request submitted successfully")
        print("⏳ Waiting for result...")
        
        result = handler.get()
        
        print("✅ Veo 3 test successful!")
        print(f"Result: {result}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Veo 3 Error: {error_msg}")
        return False

if __name__ == "__main__":
    print("🚀 Direct FAL.ai API Testing")
    print("=" * 50)
    
    # Test Sora 2 first
    sora2_success = test_fal_key()
    
    if sora2_success:
        # Test Veo 3 if Sora 2 works
        veo3_success = test_veo3()
        
        if sora2_success and veo3_success:
            print("\n✅ ALL FAL TESTS PASSED - Both models working!")
        else:
            print("\n⚠️ PARTIAL SUCCESS - Sora 2 works, Veo 3 has issues")
    else:
        print("\n❌ FAL AUTHENTICATION FAILED - Key not working")
        
    print("\n" + "=" * 50)