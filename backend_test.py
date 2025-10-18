import requests
import sys
import json
import time
from datetime import datetime
import base64
import io
from PIL import Image

class VideoGenAPITester:
    def __init__(self, base_url="https://videofusion-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", error=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {error}")
        
        self.test_results.append({
            "test_name": name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=timeout)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    details = f"Status: {response.status_code}, Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}..."
                self.log_test(name, True, details)
                return True, response_data if 'response_data' in locals() else {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                self.log_test(name, False, error=error_msg)
                return False, {}

        except Exception as e:
            self.log_test(name, False, error=f"Exception: {str(e)}")
            return False, {}

    def create_test_image(self):
        """Create a simple test image"""
        img = Image.new('RGB', (300, 300), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        return img_buffer

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_image_upload(self):
        """Test image upload to Cloudinary"""
        test_image = self.create_test_image()
        files = {'file': ('test.jpg', test_image, 'image/jpeg')}
        
        success, response = self.run_test(
            "Image Upload to Cloudinary", 
            "POST", 
            "images/upload", 
            200, 
            files=files,
            timeout=60
        )
        
        if success and response.get('success') and response.get('image_url'):
            self.uploaded_image_url = response['image_url']
            print(f"   ✅ Image uploaded successfully: {self.uploaded_image_url}")
            return True, response
        else:
            print(f"   ❌ Image upload failed")
            return False, {}

    def test_image_analysis(self, image_url):
        """Test Gemini image analysis with timeout handling"""
        print(f"\n🔍 Testing Gemini Image Analysis (30s timeout)...")
        
        success, response = self.run_test(
            "Gemini Image Analysis", 
            "POST", 
            "images/analyze", 
            200, 
            data={"image_url": image_url},
            timeout=35  # Slightly longer than backend timeout
        )
        
        if success and response.get('success'):
            analysis = response.get('analysis', {})
            if analysis:
                print(f"   ✅ Analysis completed:")
                print(f"      - Description: {analysis.get('description', 'N/A')}")
                print(f"      - Subject Type: {analysis.get('subject_type', 'N/A')}")
                print(f"      - Premium Model: {analysis.get('recommended_model_premium', 'N/A')}")
                print(f"      - Economic Model: {analysis.get('recommended_model_economico', 'N/A')}")
                return True, response
            else:
                print(f"   ⚠️ Analysis returned but no analysis data")
                return False, {}
        else:
            print(f"   ❌ Analysis failed")
            return False, {}

    def test_voices_endpoint(self):
        """Test ElevenLabs voices endpoint"""
        return self.run_test("ElevenLabs Voices", "GET", "audio/voices", 200)

    def test_audio_generation(self):
        """Test ElevenLabs audio generation"""
        audio_data = {
            "text": "Olá, este é um teste de geração de áudio em português brasileiro.",
            "voice_id": "cgSgspJ2msm6clMCkdW9",
            "stability": 0.5,
            "similarity_boost": 0.75,
            "speed": 1.0,
            "style": 0.0
        }
        
        success, response = self.run_test(
            "ElevenLabs Audio Generation", 
            "POST", 
            "audio/generate", 
            200, 
            data=audio_data,
            timeout=60
        )
        
        if success and response.get('success') and response.get('audio_url'):
            self.generated_audio_url = response['audio_url']
            print(f"   ✅ Audio generated successfully, cost: ${response.get('cost', 0):.2f}")
            return True, response
        else:
            print(f"   ❌ Audio generation failed")
            return False, {}

    def test_cost_estimation(self):
        """Test video cost estimation for both modes"""
        # Test Premium mode
        premium_data = {
            "model": "veo3",
            "mode": "premium",
            "duration": 5,
            "with_audio": True
        }
        
        success_premium, response_premium = self.run_test(
            "Cost Estimation - Premium Mode", 
            "POST", 
            "video/estimate-cost", 
            200, 
            data=premium_data
        )
        
        # Test Economic mode
        economic_data = {
            "model": "open-sora",
            "mode": "economico",
            "duration": 5,
            "with_audio": False
        }
        
        success_economic, response_economic = self.run_test(
            "Cost Estimation - Economic Mode", 
            "POST", 
            "video/estimate-cost", 
            200, 
            data=economic_data
        )
        
        if success_premium and success_economic:
            premium_cost = response_premium.get('estimated_cost', 0)
            economic_cost = response_economic.get('estimated_cost', 0)
            print(f"   ✅ Premium cost: ${premium_cost}, Economic cost: ${economic_cost}")
            return True, {"premium": response_premium, "economic": response_economic}
        
        return False, {}

    def test_admin_auth(self):
        """Test admin password verification"""
        # Test correct password
        correct_data = {"password": "mauricio123"}
        success_correct, _ = self.run_test(
            "Admin Auth - Correct Password", 
            "POST", 
            "auth/verify", 
            200, 
            data=correct_data
        )
        
        # Test incorrect password
        incorrect_data = {"password": "wrongpassword"}
        success_incorrect, _ = self.run_test(
            "Admin Auth - Incorrect Password", 
            "POST", 
            "auth/verify", 
            401, 
            data=incorrect_data
        )
        
        return success_correct and success_incorrect

    def test_gallery_endpoints(self):
        """Test gallery-related endpoints"""
        # Test getting gallery items
        success, response = self.run_test(
            "Gallery Items", 
            "GET", 
            "gallery/items", 
            200
        )
        
        if success:
            videos = response.get('videos', [])
            audios = response.get('audios', [])
            images = response.get('images', [])
            print(f"   ✅ Gallery loaded: {len(videos)} videos, {len(audios)} audios, {len(images)} images")
            return True, response
        
        return False, {}

    def test_token_usage(self):
        """Test token usage statistics"""
        return self.run_test("Token Usage Statistics", "GET", "tokens/usage", 200)

    def run_comprehensive_test(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend API Testing")
        print("=" * 60)
        
        # Basic connectivity
        self.test_root_endpoint()
        
        # Image workflow
        upload_success, upload_response = self.test_image_upload()
        if upload_success:
            image_url = upload_response.get('image_url')
            if image_url:
                self.test_image_analysis(image_url)
        
        # Audio workflow
        self.test_voices_endpoint()
        self.test_audio_generation()
        
        # Cost estimation
        self.test_cost_estimation()
        
        # Admin functionality
        self.test_admin_auth()
        
        # Gallery functionality
        self.test_gallery_endpoints()
        
        # Usage statistics
        self.test_token_usage()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed < self.tests_run:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test_name']}: {result['error']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = VideoGenAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())