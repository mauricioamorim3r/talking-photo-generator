"""
Test Gemini 2.5 Flash Image generation
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_gemini_image_generation():
    """Test image generation with Gemini 2.5 Flash Image"""

    print("=" * 80)
    print("Testing Gemini 2.5 Flash Image Generation")
    print("=" * 80)

    import google.generativeai as genai
    from PIL import Image
    import base64
    from io import BytesIO

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv("backend/.env")

    gemini_key = os.getenv("GEMINI_KEY")
    if not gemini_key:
        print("ERROR: GEMINI_KEY not found in environment")
        return False

    print(f"\n1. Gemini API Key: {'*' * 20}{gemini_key[-4:]}")

    # Configure Gemini
    genai.configure(api_key=gemini_key)

    # Test 1: Simple text-to-image generation
    print("\n" + "=" * 80)
    print("TEST 1: Simple Text-to-Image Generation")
    print("=" * 80)

    try:
        prompt = "A cute cartoon banana wearing sunglasses at the beach"
        print(f"Prompt: {prompt}")

        # Configure generation settings
        generation_config = {
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Create model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-image",
            generation_config=generation_config
        )

        print("\nGenerating image...")
        response = model.generate_content([prompt])

        # Extract image
        image_found = False
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_bytes = part.inline_data.data
                image_data = base64.b64encode(image_bytes).decode('utf-8')
                mime_type = part.inline_data.mime_type

                print(f"\nSUCCESS! Image generated:")
                print(f"  - Size: {len(image_data)} chars")
                print(f"  - MIME type: {mime_type}")
                print(f"  - Preview: data:{mime_type};base64,{image_data[:50]}...")

                # Save to file for inspection
                with open("test_gemini_output_text2img.png", "wb") as f:
                    f.write(image_bytes)
                print(f"  - Saved to: test_gemini_output_text2img.png")

                image_found = True
                break

        if not image_found:
            print("\nERROR: No image found in response")
            print(f"Response: {response}")
            return False

    except Exception as e:
        print(f"\nERROR in Test 1: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Image-to-image generation with reference image
    print("\n" + "=" * 80)
    print("TEST 2: Image-to-Image Generation (with reference)")
    print("=" * 80)

    try:
        # Create a simple test image
        print("\nCreating test reference image...")
        test_image = Image.new('RGB', (512, 512), color='blue')

        # Save for reference
        test_image.save("test_reference_image.png")
        print("  - Saved test reference: test_reference_image.png")

        prompt = "Transform this image into a sunset landscape with mountains"
        print(f"Prompt: {prompt}")

        content_parts = [test_image, prompt]

        print("\nGenerating image with reference...")
        response = model.generate_content(content_parts)

        # Extract image
        image_found = False
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_bytes = part.inline_data.data
                image_data = base64.b64encode(image_bytes).decode('utf-8')
                mime_type = part.inline_data.mime_type

                print(f"\nSUCCESS! Image generated:")
                print(f"  - Size: {len(image_data)} chars")
                print(f"  - MIME type: {mime_type}")

                # Save to file for inspection
                with open("test_gemini_output_img2img.png", "wb") as f:
                    f.write(image_bytes)
                print(f"  - Saved to: test_gemini_output_img2img.png")

                image_found = True
                break

        if not image_found:
            print("\nERROR: No image found in response")
            return False

    except Exception as e:
        print(f"\nERROR in Test 2: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    result = asyncio.run(test_gemini_image_generation())
    sys.exit(0 if result else 1)
