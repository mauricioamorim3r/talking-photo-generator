#!/usr/bin/env python3
"""
Script para atualizar a configuração do frontend no Render
"""
import requests
import json

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# 1. Obter ID do serviço
print("🔍 Buscando ID do serviço...\n")
response = requests.get("https://api.render.com/v1/services", headers=headers)

service_id = None
for item in response.json():
    service = item.get("service", {})
    if service.get("name") == "talking-photo-frontend":
        service_id = service.get("id")
        print(f"✅ Serviço encontrado!")
        print(f"📝 ID: {service_id}\n")
        break

if not service_id:
    print("❌ Serviço não encontrado!")
    exit(1)

# 2. Atualizar configuração
print("🔧 Atualizando configuração do frontend...\n")

update_payload = {
    "buildCommand": "npm install --legacy-peer-deps && npm run build",
    "publishPath": "build"
}

update_url = f"https://api.render.com/v1/services/{service_id}"
response = requests.patch(update_url, headers=headers, json=update_payload)

print(f"📊 Status: {response.status_code}")

if response.status_code == 200:
    print("✅ Configuração atualizada com sucesso!\n")
    
    updated = response.json()
    details = updated.get("serviceDetails", {})
    
    print("--- NOVA CONFIGURAÇÃO ---")
    print(f"🔨 Build Command: {details.get('buildCommand')}")
    print(f"📁 Publish Path: {details.get('publishPath')}")
    
    print("\n🚀 Iniciando novo deploy...")
    
    # 3. Trigger manual deploy
    deploy_url = f"https://api.render.com/v1/services/{service_id}/deploys"
    deploy_response = requests.post(deploy_url, headers=headers, json={})
    
    if deploy_response.status_code in [200, 201]:
        deploy = deploy_response.json()
        print(f"✅ Deploy iniciado!")
        print(f"📝 Deploy ID: {deploy.get('id', 'N/A')}")
        print(f"📊 Status: {deploy.get('status', 'N/A')}")
        print(f"\n⏳ O build levará cerca de 5-8 minutos...")
        print(f"🔗 Acompanhe: https://dashboard.render.com/static/{service_id}")
    else:
        print(f"⚠️  Não foi possível iniciar deploy: {deploy_response.status_code}")
        print("💡 Você pode iniciar manualmente no Dashboard")
else:
    print(f"❌ Erro ao atualizar: {response.text}")
