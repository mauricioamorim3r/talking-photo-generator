"""
Check if frontend service needs to be recreated as static site
"""
import requests
import os

API_KEY = os.getenv("RENDER_API_KEY", "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S")
SERVICE_ID = "srv-d3qd08ali9vc73c8a5f0"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

print("🔍 Verificando configuração do serviço frontend...\n")

response = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    service_type = data.get("service", {}).get("type")
    name = data.get("service", {}).get("name")
    
    print(f"📋 Serviço: {name}")
    print(f"🔧 Tipo atual: {service_type}")
    print(f"🆔 ID: {SERVICE_ID}\n")
    
    if service_type == "static_site":
        print("✅ Serviço já é do tipo 'static_site'!")
        print("   O _redirects file deve funcionar agora.")
    elif service_type == "web_service":
        print("⚠️  Serviço ainda é do tipo 'web_service'")
        print("\n📝 AÇÃO NECESSÁRIA:")
        print("   1. Acesse: https://dashboard.render.com/static/srv-d3qd08ali9vc73c8a5f0")
        print("   2. Ou RECRIE o serviço:")
        print("      - Delete o serviço atual")
        print("      - Crie novo 'Static Site' com:")
        print("        • Build Command: cd frontend && npm install --legacy-peer-deps && npm run build")
        print("        • Publish Directory: frontend/build")
        print("        • Auto-deploy: Yes")
    else:
        print(f"❓ Tipo desconhecido: {service_type}")
else:
    print(f"❌ Erro ao buscar serviço: {response.status_code}")
    print(f"   {response.text}")
