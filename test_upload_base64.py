import requests
import base64
from PIL import Image
import io

API = "https://gerador-fantasia.onrender.com/api"

print("🧪 Testando novo endpoint de upload Base64...")

# Create test image
img = Image.new('RGB', (100, 100), color='blue')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Convert to base64
base64_image = base64.b64encode(img_bytes.read()).decode('utf-8')
base64_with_prefix = f"data:image/jpeg;base64,{base64_image}"

print(f"📦 Image size: {len(base64_image)} base64 chars")
print(f"📤 Sending POST to {API}/images/upload...")

# Send as JSON (not FormData)
response = requests.post(
    f"{API}/images/upload",
    json={"image_data": base64_with_prefix},
    timeout=30
)

print(f"\n📊 Status: {response.status_code}")
print(f"📄 Headers: {dict(response.headers)}")
print(f"📝 Body: {response.text}")

if response.status_code == 200:
    data = response.json()
    print("\n✅ SUCESSO! Upload funcionou!")
    print(f"   Format: {data.get('format')}")
    print(f"   Size: {data.get('size_bytes')} bytes")
    print(f"   Base64 retornado: {len(data.get('image_data', ''))} chars")
else:
    print("\n❌ ERRO!")
