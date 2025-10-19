#!/usr/bin/env python3
"""
Script para criar o Static Site do frontend no Render via API
"""
import requests
import json

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
API_URL = "https://api.render.com/v1/services"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "type": "static_site",
    "name": "talking-photo-frontend",
    "ownerId": "tea-d1ddrs6mcj7s73fp6nd0",
    "repo": "https://github.com/mauricioamorim3r/talking-photo-generator",
    "autoDeploy": "yes",
    "branch": "main",
    "rootDir": "frontend",
    "buildCommand": "npm install --legacy-peer-deps && npm run build",
    "publishPath": "build",
    "envVars": [
        {
            "key": "REACT_APP_API_URL",
            "value": "https://gerador-fantasia.onrender.com"
        }
    ]
}

print("🚀 Criando Static Site no Render...")
print(f"📦 Payload: {json.dumps(payload, indent=2)}")
print("\n⏳ Enviando requisição...\n")

try:
    response = requests.post(API_URL, headers=headers, json=payload)
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response:\n{json.dumps(response.json(), indent=2)}")
    
    if response.status_code in [200, 201]:
        service = response.json()
        print("\n✅ Frontend criado com sucesso!")
        print(f"🌐 URL: {service.get('service', {}).get('serviceDetails', {}).get('url', 'N/A')}")
        print(f"🔗 Dashboard: {service.get('service', {}).get('dashboardUrl', 'N/A')}")
        print(f"📝 Nome: {service.get('service', {}).get('name', 'N/A')}")
    else:
        print("\n❌ Erro ao criar serviço!")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")
