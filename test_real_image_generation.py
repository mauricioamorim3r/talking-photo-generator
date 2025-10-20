"""
Test Gemini 2.5 Flash Image generation with real image
Simulates the complete flow: upload image → send to API → get result
"""
import asyncio
import base64
import json
import sys
from pathlib import Path
import aiohttp
import os

async def test_real_image_generation():
    """Test image generation with a real reference image"""

    print("=" * 80)
    print("Testing Gemini 2.5 Flash Image - Real World Scenario")
    print("=" * 80)

    # Backend URL
    BACKEND_URL = "http://localhost:8001"

    # Check if backend is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    print("\n[ERROR] Backend is not running!")
                    print("   Please start the backend first: start-backend.bat")
                    return False
                print("\n[OK] Backend is running")
    except Exception as e:
        print(f"\n[ERROR] Cannot connect to backend: {str(e)}")
        print("   Please start the backend first: start-backend.bat")
        return False

    # Find a test image
    test_images = [
        Path("backend/uploads/d6868289-9a0f-42ba-a77e-47a10a19aa06.jpg"),
        Path("backend/uploads/3e53f1ec-afb3-4eac-bb5a-63754614cfe6.png"),
        Path("test_image.jpg")
    ]

    test_image = None
    for img_path in test_images:
        if img_path.exists():
            test_image = img_path
            break

    if not test_image:
        print("\n[WARNING] No test image found. Please provide a test image.")
        print("   You can:")
        print("   1. Copy a portrait image to 'test_image.jpg' in the project root")
        print("   2. Or upload an image via the web interface first")
        return False

    print(f"\n[IMAGE] Using test image: {test_image}")

    # Read and convert to base64
    with open(test_image, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        # Detect mime type
        if test_image.suffix.lower() in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif test_image.suffix.lower() == '.png':
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'

        image_data_url = f"data:{mime_type};base64,{image_base64}"

    print(f"   Size: {len(image_bytes)} bytes")
    print(f"   Base64 size: {len(image_base64)} chars")

    # Test prompts from the library
    test_prompts = [
        {
            "name": "Retrato em Pixel Art",
            "prompt": "Transforme este retrato em um avatar de videogame de 16-bits, estilo pixel art, com uma caixa de diálogo abaixo."
        },
        {
            "name": "Viagem no Tempo Anos 80",
            "prompt": "Recrie esta foto como se tivesse sido tirada nos anos 80, com estética de filme Kodachrome, roupas e cabelo da época."
        },
        {
            "name": "Retrato em Aquarela",
            "prompt": "Transforme este retrato em uma pintura de aquarela, com pinceladas visíveis e cores suaves."
        }
    ]

    # Test each prompt
    for i, test_case in enumerate(test_prompts, 1):
        print("\n" + "=" * 80)
        print(f"TEST {i}: {test_case['name']}")
        print("=" * 80)
        print(f"Prompt: {test_case['prompt']}")

        # Prepare request
        request_data = {
            "prompt": test_case['prompt'],
            "reference_image_base64": image_data_url
        }

        try:
            print("\n[GENERATE] Sending request to /api/images/generate...")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/images/generate",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=120)  # 2 minutes timeout
                ) as resp:
                    response_text = await resp.text()

                    if resp.status != 200:
                        print(f"\n[ERROR] HTTP {resp.status}")
                        print(f"   Response: {response_text[:500]}")
                        continue

                    result = json.loads(response_text)

                    if not result.get('success'):
                        print(f"\n[ERROR] Generation failed")
                        print(f"   Response: {result}")
                        continue

                    print(f"\n[SUCCESS] Image generated!")
                    print(f"   Image ID: {result['image_id']}")
                    print(f"   Cost: ${result['cost']}")
                    print(f"   Prompt: {result['prompt'][:50]}...")

                    # Extract and save the image
                    image_url = result['image_url']
                    if image_url.startswith('data:'):
                        # Extract base64 data
                        _, base64_data = image_url.split(',', 1)
                        output_bytes = base64.b64decode(base64_data)

                        # Save to file
                        output_filename = f"test_output_{i}_{test_case['name'].replace(' ', '_')}.png"
                        with open(output_filename, "wb") as f:
                            f.write(output_bytes)

                        print(f"   [SAVED] {output_filename}")
                        print(f"   Size: {len(output_bytes)} bytes ({len(base64_data)} chars base64)")
                    else:
                        print(f"   Image URL: {image_url[:100]}...")

        except asyncio.TimeoutError:
            print(f"\n[TIMEOUT] Generation took too long (>120s)")
            continue
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print("\n[FILES] Check the generated images in the project root:")
    print("   - test_output_1_*.png")
    print("   - test_output_2_*.png")
    print("   - test_output_3_*.png")
    print("\nCompare them with the Google AI Studio results!")

    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_real_image_generation())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
        sys.exit(1)
