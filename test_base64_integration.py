import requests
import base64
from PIL import Image
import io

API = "https://gerador-fantasia.onrender.com/api"
FRONTEND = "https://foto-video-fantasia.onrender.com"

print("🔥 Acordando serviços...")
print(f"Backend: {API}")
print(f"Frontend: {FRONTEND}")

# Wake backend
for i in range(3):
    try:
        response = requests.get(f"{API.replace('/api', '')}/health", timeout=10)
        print(f"  Backend attempt {i+1}: {response.status_code}")
    except Exception as e:
        print(f"  Backend attempt {i+1}: Error - {str(e)}")

# Check frontend
try:
    response = requests.get(FRONTEND, timeout=10)
    print(f"  Frontend: {response.status_code}")
except Exception as e:
    print(f"  Frontend: Error - {str(e)}")

print("\n🧪 Testando upload Base64...")

# Create test image
img = Image.new('RGB', (150, 150), color='green')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Convert to base64
base64_image = base64.b64encode(img_bytes.read()).decode('utf-8')
base64_with_prefix = f"data:image/png;base64,{base64_image}"

print(f"📦 Image size: {len(base64_image)} chars")

# Test upload
response = requests.post(
    f"{API}/images/upload",
    json={"image_data": base64_with_prefix},
    timeout=30
)

print(f"📊 Upload Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ UPLOAD FUNCIONOU!")
    print(f"   Format: {data.get('format')}")
    print(f"   Size: {data.get('size_bytes')} bytes")
else:
    print(f"❌ ERRO: {response.text}")

print("\n🎨 Testando geração de imagem...")

# Test image generation
response = requests.post(
    f"{API}/images/generate",
    json={
        "prompt": "A beautiful sunset over the ocean, cinematic, high quality"
    },
    timeout=60
)

print(f"📊 Generation Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ GERAÇÃO FUNCIONOU!")
    print(f"   Image URL: {data.get('image_url', '')[:100]}...")
    print(f"   Image ID: {data.get('image_id')}")
else:
    print(f"❌ ERRO: {response.text}")

print("\n✅ Todos os testes completos!")
