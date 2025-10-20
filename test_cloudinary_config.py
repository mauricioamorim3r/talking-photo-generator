import requests
import os

# Teste direto das credenciais Cloudinary configuradas no Render
API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
SERVICE_ID = "srv-d3q80d0gjchc73b48p40"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

print("=" * 70)
print("🔍 VERIFICANDO VARIÁVEIS DE AMBIENTE DO CLOUDINARY")
print("=" * 70)

# Buscar env vars
response = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    env_vars = data if isinstance(data, list) else data.get('envVars', [])
    
    cloudinary_vars = [
        var for var in env_vars 
        if var.get('key', '').startswith('CLOUDINARY')
    ]
    
    print(f"\n📋 Variáveis Cloudinary encontradas: {len(cloudinary_vars)}")
    for var in cloudinary_vars:
        key = var['key']
        value = var.get('value', 'N/A')
        
        # Mostrar apenas primeiros/últimos caracteres para segurança
        if len(value) > 8:
            masked = f"{value[:4]}...{value[-4:]}"
        else:
            masked = "***"
            
        print(f"  • {key}: {masked}")
        
    # Verificar se tem upload preset
    has_preset = any(var['key'] == 'CLOUDINARY_UPLOAD_PRESET' for var in cloudinary_vars)
    has_cloud_name = any(var['key'] == 'CLOUDINARY_CLOUD_NAME' for var in cloudinary_vars)
    has_api_key = any(var['key'] == 'CLOUDINARY_API_KEY' for var in cloudinary_vars)
    has_api_secret = any(var['key'] == 'CLOUDINARY_API_SECRET' for var in cloudinary_vars)
    
    print("\n✅ Status:")
    print(f"  • CLOUD_NAME: {'✓' if has_cloud_name else '✗'}")
    print(f"  • API_KEY: {'✓' if has_api_key else '✗'}")
    print(f"  • API_SECRET: {'✓' if has_api_secret else '✗'}")
    print(f"  • UPLOAD_PRESET: {'✓' if has_preset else '✗ (opcional)'}")
    
    if has_preset:
        preset_var = next(var for var in cloudinary_vars if var['key'] == 'CLOUDINARY_UPLOAD_PRESET')
        preset_value = preset_var.get('value', '')
        print(f"\n⚠️  UPLOAD_PRESET configurado: {preset_value}")
        print("   Mas nosso código NÃO está usando ele!")
        print("   Isso pode estar causando conflito.")
        
else:
    print(f"❌ Erro ao buscar env vars: {response.status_code}")
    print(f"   {response.text}")

print("=" * 70)
