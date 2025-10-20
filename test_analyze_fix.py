import requests
import base64
from PIL import Image
import io

API = "https://gerador-fantasia.onrender.com/api"

print("🔥 Acordando backend...")
for i in range(3):
    r = requests.get(f"{API}/../health", timeout=10)
    print(f"  Attempt {i+1}: {r.status_code}")

print("\n🧪 Testando upload + analyze com Base64...")

# Create test image
img = Image.new('RGB', (100, 100), color='green')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Convert to base64
base64_image = base64.b64encode(img_bytes.read()).decode('utf-8')
base64_with_prefix = f"data:image/jpeg;base64,{base64_image}"

# Test upload
print("\n1️⃣ Testing upload...")
upload_response = requests.post(
    f"{API}/images/upload",
    json={"image_data": base64_with_prefix},
    timeout=30
)
print(f"   Upload Status: {upload_response.status_code}")

if upload_response.status_code == 200:
    print("   ✅ Upload OK!")
    
    # Test analyze
    print("\n2️⃣ Testing analyze...")
    analyze_response = requests.post(
        f"{API}/images/analyze",
        json={"image_data": base64_with_prefix},
        timeout=60
    )
    print(f"   Analyze Status: {analyze_response.status_code}")
    
    if analyze_response.status_code == 200:
        data = analyze_response.json()
        print("   ✅ Analyze OK!")
        print(f"   Suggested model: {data.get('analysis', {}).get('recommended_model_premium', 'N/A')}")
    else:
        print(f"   ❌ Analyze failed: {analyze_response.text[:200]}")
else:
    print(f"   ❌ Upload failed: {upload_response.text[:200]}")

print("\n✅ Test complete!")
