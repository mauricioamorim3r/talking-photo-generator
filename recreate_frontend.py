#!/usr/bin/env python3
"""
Script para deletar e recriar o frontend com configuração correta
"""
import requests
import json
import time

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
SERVICE_ID = "srv-d3q9r8odl3ps73bp1p8g"
OWNER_ID = "tea-d1ddrs6mcj7s73fp6nd0"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🔄 RECRIANDO FRONTEND COM CONFIGURAÇÃO CORRETA")
print("=" * 70)

# PASSO 1: Deletar serviço existente
print("\n1️⃣ Deletando serviço existente...")
print(f"   📝 Service ID: {SERVICE_ID}")

delete_url = f"https://api.render.com/v1/services/{SERVICE_ID}"
delete_response = requests.delete(delete_url, headers=headers)

if delete_response.status_code == 204:
    print("   ✅ Serviço deletado com sucesso!")
elif delete_response.status_code == 404:
    print("   ⚠️  Serviço já foi deletado ou não existe")
else:
    print(f"   ❌ Erro ao deletar: {delete_response.status_code}")
    print(f"   {delete_response.text}")
    exit(1)

print("   ⏳ Aguardando 3 segundos...")
time.sleep(3)

# PASSO 2: Criar novo serviço com configuração correta
print("\n2️⃣ Criando novo Static Site com configuração correta...")

# Payload correto para Static Site
create_payload = {
    "type": "static_site",
    "name": "talking-photo-frontend",
    "ownerId": OWNER_ID,
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

print(f"\n📦 Configuração:")
print(f"   • Nome: talking-photo-frontend")
print(f"   • Tipo: static_site")
print(f"   • Repo: mauricioamorim3r/talking-photo-generator")
print(f"   • Branch: main")
print(f"   • Root: frontend")
print(f"   • Build: npm install --legacy-peer-deps && npm run build")
print(f"   • Publish: build")
print(f"   • Env: REACT_APP_API_URL")

create_url = "https://api.render.com/v1/services"
create_response = requests.post(create_url, headers=headers, json=create_payload)

print(f"\n📊 Status: {create_response.status_code}")

if create_response.status_code in [200, 201]:
    service_data = create_response.json()
    service = service_data.get("service", service_data)
    
    new_service_id = service.get("id")
    dashboard_url = service.get("dashboardUrl")
    service_url = service.get("serviceDetails", {}).get("url")
    
    print("\n" + "=" * 70)
    print("✅ FRONTEND CRIADO COM SUCESSO!")
    print("=" * 70)
    print(f"\n📝 Service ID: {new_service_id}")
    print(f"🌐 URL: {service_url}")
    print(f"🔗 Dashboard: {dashboard_url}")
    
    # Verificar configuração
    details = service.get("serviceDetails", {})
    print(f"\n--- CONFIGURAÇÃO APLICADA ---")
    print(f"🔨 Build Command: {details.get('buildCommand', 'N/A')}")
    print(f"📁 Publish Path: {details.get('publishPath', 'N/A')}")
    print(f"📂 Root Dir: {service.get('rootDir', '(root)')}")
    print(f"🌿 Branch: {service.get('branch', 'N/A')}")
    print(f"🚀 Auto Deploy: {service.get('autoDeploy', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("⏳ DEPLOY INICIADO AUTOMATICAMENTE")
    print("=" * 70)
    print(f"\n⏱️  Tempo estimado: 5-8 minutos")
    print(f"🔗 Acompanhe: {dashboard_url}")
    
    # Salvar novo service ID
    with open("frontend_service_id.txt", "w") as f:
        f.write(new_service_id)
    
    print(f"\n💾 Service ID salvo em: frontend_service_id.txt")
    print(f"\n💡 Execute 'python monitor_deploy.py' para monitorar o progresso")
    print("   (Ajuste o SERVICE_ID no script para: {})".format(new_service_id))
    
elif create_response.status_code == 400:
    error_data = create_response.json()
    print(f"\n❌ Erro de validação: {error_data.get('message', 'N/A')}")
    print("\n💡 Possíveis causas:")
    print("   1. Nome ainda não está disponível (aguarde alguns minutos)")
    print("   2. Parâmetros inválidos no payload")
    print(f"\n📄 Response completa:")
    print(json.dumps(error_data, indent=2))
    
else:
    print(f"\n❌ Erro ao criar serviço: {create_response.status_code}")
    print(create_response.text)

print("\n" + "=" * 70)
