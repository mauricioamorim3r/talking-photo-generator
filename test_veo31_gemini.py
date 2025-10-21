"""
Test Veo 3.1 via Gemini API
Official Google implementation using google-genai SDK
"""

import os
import sys
from pathlib import Path
from PIL import Image
import io

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

from veo31_gemini import Veo31GeminiGenerator

def test_text_to_video():
    """Test text-to-video generation"""
    print("\n" + "="*80)
    print("TEST 1: Text-to-Video Generation")
    print("="*80)
    
    generator = Veo31GeminiGenerator()
    
    prompt = """A cinematic shot of a majestic lion walking through the African savannah 
    at golden hour. The camera follows the lion as it moves gracefully through tall grass, 
    with warm sunset lighting creating a dramatic atmosphere."""
    
    video_path = generator.generate_video_text_only(
        prompt=prompt,
        duration_seconds=8,
        resolution="720p",
        aspect_ratio="16:9",
        output_path="test_veo31_text_only.mp4"
    )
    
    print(f"\n✅ Video generated: {video_path}")
    return video_path

def test_image_to_video():
    """Test image-to-video generation"""
    print("\n" + "="*80)
    print("TEST 2: Image-to-Video Generation")
    print("="*80)
    
    # Create a test image
    test_image_path = "test_input_image.jpg"
    
    if not os.path.exists(test_image_path):
        print("📸 Creating test image...")
        img = Image.new('RGB', (1280, 720), color=(70, 130, 180))  # Sky blue
        
        # Add a simple gradient
        pixels = img.load()
        for y in range(720):
            for x in range(1280):
                r = int(70 + (255 - 70) * (y / 720))
                g = int(130 + (200 - 130) * (y / 720))
                b = int(180 + (150 - 180) * (y / 720))
                pixels[x, y] = (r, g, b)
        
        img.save(test_image_path, 'JPEG')
        print(f"✅ Test image created: {test_image_path}")
    
    # Generate video
    generator = Veo31GeminiGenerator()
    
    prompt = """Dramatic time-lapse of clouds moving across a beautiful gradient sky, 
    from sunrise to sunset. The colors shift smoothly from cool blues to warm oranges 
    and purples. Cinematic, peaceful, 4K quality."""
    
    video_path = generator.generate_video_from_image(
        prompt=prompt,
        image_path=test_image_path,
        duration_seconds=8,
        resolution="720p",
        aspect_ratio="16:9",
        output_path="test_veo31_image_to_video.mp4"
    )
    
    print(f"\n✅ Video generated: {video_path}")
    return video_path

def test_with_negative_prompt():
    """Test text-to-video with negative prompt"""
    print("\n" + "="*80)
    print("TEST 3: Text-to-Video with Negative Prompt")
    print("="*80)
    
    generator = Veo31GeminiGenerator()
    
    prompt = """A beautiful woman with flowing hair walking through a serene garden 
    filled with colorful flowers. Soft natural lighting, cinematic composition."""
    
    negative_prompt = "cartoon, drawing, low quality, blurry, distorted"
    
    video_path = generator.generate_video_text_only(
        prompt=prompt,
        duration_seconds=6,
        resolution="720p",
        aspect_ratio="9:16",  # Vertical for social media
        negative_prompt=negative_prompt,
        output_path="test_veo31_negative_prompt.mp4"
    )
    
    print(f"\n✅ Video generated: {video_path}")
    return video_path

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎬 Veo 3.1 Gemini API - Complete Test Suite")
    print("="*80)
    
    # Check API key
    api_key = os.getenv("GEMINI_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_KEY not found in environment variables!")
        print("Please set GEMINI_KEY in backend/.env")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    try:
        # Test 1: Text-to-video (simple)
        print("\nStarting Test 1...")
        test_text_to_video()
        
        # Test 2: Image-to-video (our main use case)
        print("\nStarting Test 2...")
        test_image_to_video()
        
        # Test 3: With negative prompt (advanced)
        # print("\nStarting Test 3...")
        # test_with_negative_prompt()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nNOTE: Each video generation can take 11 seconds to 6 minutes.")
        print("Check the generated .mp4 files in the current directory.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
