#!/usr/bin/env python3
"""
Create NEW Web Service with 'serve' for SPA routing (different name)
"""
import requests
import json

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
API_URL = "https://api.render.com/v1/services"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Web service with 'serve' for SPA routing - NEW NAME
payload = {
    "type": "web_service",
    "name": "foto-video-fantasia-v2",  # Different name
    "ownerId": "tea-d1ddrs6mcj7s73fp6nd0",
    "repo": "https://github.com/mauricioamorim3r/talking-photo-generator",
    "autoDeploy": "yes",
    "branch": "main",
    "rootDir": "frontend",
    "buildCommand": "npm install --legacy-peer-deps && npm install -g serve && npm run build",
    "serviceDetails": {
        "env": "node",
        "plan": "starter",
        "region": "oregon"
    },
    "startCommand": "serve -s build -l $PORT",
    "envVars": [
        {
            "key": "NODE_VERSION",
            "value": "18.17.0"
        },
        {
            "key": "REACT_APP_API_URL",
            "value": "https://gerador-fantasia.onrender.com"
        }
    ]
}

print("🚀 Criando Web Service com 'serve' para SPA routing...")
print(f"📝 Nome: {payload['name']}")
print(f"🔧 Start Command: {payload['startCommand']}")
print("\n⏳ Enviando requisição...\n")

try:
    response = requests.post(API_URL, headers=headers, json=payload)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        service = response.json()
        service_data = service.get('service', {})
        service_id = service_data.get('id', 'N/A')
        service_url = service_data.get('serviceDetails', {}).get('url', 'N/A')
        
        print("✅ Frontend Web Service criado com sucesso!\n")
        print(f"🆔 Service ID: {service_id}")
        print(f"🌐 URL: {service_url}")
        print(f"🔗 Dashboard: {service_data.get('dashboardUrl', 'N/A')}")
        print(f"📝 Nome: {service_data.get('name', 'N/A')}")
        print("\n💡 'serve' automaticamente lida com SPA routing!")
        print("   - Todas as rotas retornam index.html")
        print("   - React Router funciona perfeitamente")
        print("   - /gallery, /image-generator, /admin devem carregar")
        
        # Save service ID
        with open("frontend_service_id_v2.txt", "w") as f:
            f.write(f"{service_id}\n{service_url}\n")
        print(f"\n💾 Info salva em frontend_service_id_v2.txt")
        
        print("\n⏳ Aguarde 2-3 minutos para o build completar")
        print(f"🔗 Acesse: {service_url}")
        
    else:
        print(f"❌ Erro ao criar serviço: {response.status_code}")
        print(f"📄 Response:\n{json.dumps(response.json(), indent=2)}")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")
