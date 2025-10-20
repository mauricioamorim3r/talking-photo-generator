import requests
import io
from PIL import Image

BACKEND_URL = "https://gerador-fantasia.onrender.com"
API = f"{BACKEND_URL}/api"

print("="*70)
print("🧪 TESTE DE UPLOAD DE IMAGEM")
print("="*70)

# Criar uma imagem de teste pequena
print("\n1️⃣ Criando imagem de teste...")
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

print("   ✅ Imagem de teste criada (100x100, vermelho)")

# Tentar fazer upload
print("\n2️⃣ Fazendo upload para o backend...")
try:
    files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
    response = requests.post(f"{API}/images/upload", files=files, timeout=30)
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📝 Response Headers:")
    for key, value in response.headers.items():
        print(f"   {key}: {value}")
    
    print(f"\n📄 Response Body:")
    print(response.text)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("\n✅ UPLOAD BEM-SUCEDIDO!")
            print(f"🔗 URL da imagem: {data.get('image_url')}")
            print(f"🆔 Cloudinary ID: {data.get('cloudinary_id')}")
        else:
            print("\n❌ Upload falhou (success=false)")
    else:
        print(f"\n❌ ERRO: Status {response.status_code}")
        try:
            error_data = response.json()
            print(f"💬 Mensagem: {error_data.get('detail', 'Sem detalhes')}")
        except:
            print(f"💬 Resposta: {response.text[:200]}")

except requests.exceptions.Timeout:
    print("\n⏱️ TIMEOUT: Backend demorou mais de 30 segundos")
    print("💡 Possível causa: Backend está hibernando")
    print("🔧 Solução: Execute 'python wake_backend.py'")

except requests.exceptions.ConnectionError as e:
    print(f"\n🔌 ERRO DE CONEXÃO: {e}")
    print("💡 Possível causa: Backend offline ou problema de rede")

except Exception as e:
    print(f"\n❌ ERRO INESPERADO: {type(e).__name__}")
    print(f"💬 Mensagem: {str(e)}")

print("\n" + "="*70)
