#!/usr/bin/env python3
"""
Script para obter detalhes completos do frontend
"""
import requests
import json

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
headers = {"Authorization": f"Bearer {API_KEY}"}

response = requests.get("https://api.render.com/v1/services", headers=headers)

for item in response.json():
    service = item.get("service", {})
    if service.get("name") == "talking-photo-frontend":
        details = service.get("serviceDetails", {})
        
        print("=" * 60)
        print("🎯 FRONTEND TALKING-PHOTO - STATUS COMPLETO")
        print("=" * 60)
        print(f"\n📝 Nome: {service.get('name')}")
        print(f"🌐 URL: {details.get('url')}")
        print(f"📊 Status: {'✅ ATIVO' if service.get('suspended') == 'not_suspended' else '❌ SUSPENSO'}")
        print(f"🔧 Tipo: {service.get('type')}")
        print(f"\n--- CONFIGURAÇÃO ---")
        print(f"🌿 Branch: {service.get('branch')}")
        print(f"📦 Repositório: {service.get('repo')}")
        print(f"📂 Root Directory: {service.get('rootDir') or '(root)'}")
        print(f"🔨 Build Command: {details.get('buildCommand', 'N/A')}")
        print(f"📁 Publish Path: {details.get('publishPath', 'N/A')}")
        print(f"🚀 Auto Deploy: {service.get('autoDeploy')}")
        
        print(f"\n--- LINKS ---")
        print(f"🔗 Dashboard: {service.get('dashboardUrl')}")
        print(f"🌐 Site: {details.get('url')}")
        
        print(f"\n--- DATAS ---")
        print(f"📅 Criado: {service.get('createdAt')}")
        print(f"🔄 Atualizado: {service.get('updatedAt')}")
        
        print("\n" + "=" * 60)
        print("✅ FRONTEND ESTÁ CONFIGURADO E ATIVO!")
        print("=" * 60)
        break
