#!/usr/bin/env python3
"""
Script para verificar se o frontend já existe e obter informações
"""
import requests
import json

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
API_URL = "https://api.render.com/v1/services"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("🔍 Buscando serviços no Render...\n")

try:
    response = requests.get(API_URL, headers=headers)
    
    if response.status_code == 200:
        services = response.json()
        
        print(f"✅ Encontrados {len(services)} serviços\n")
        
        # Buscar por talking-photo ou frontend
        frontend_found = None
        
        for item in services:
            service = item.get('service', {})
            name = service.get('name', '')
            
            if 'talking-photo' in name.lower() or (name.lower().endswith('frontend') and 'talking' in name.lower()):
                frontend_found = service
                print(f"🎯 FRONTEND ENCONTRADO!")
                print(f"📝 Nome: {name}")
                print(f"🌐 URL: {service.get('serviceDetails', {}).get('url', 'N/A')}")
                print(f"🔗 Dashboard: {service.get('dashboardUrl', 'N/A')}")
                print(f"📊 Status: {service.get('suspended', 'active')}")
                print(f"🔧 Tipo: {service.get('type', 'N/A')}")
                print(f"🌿 Branch: {service.get('branch', 'N/A')}")
                break
        
        if not frontend_found:
            print("❌ Serviço 'talking-photo-frontend' não encontrado nos serviços ativos.")
            print("\n💡 O nome já está em uso. Pode estar em um dos seguintes estados:")
            print("   1. Serviço deletado recentemente (nome reservado por 30 dias)")
            print("   2. Serviço em outra conta/time")
            print("   3. Serviço suspenso")
            print("\n🔧 Soluções:")
            print("   1. Use outro nome: 'gerador-fantasia-frontend'")
            print("   2. Aguarde 30 dias se foi deletado")
            print("   3. Verifique no Dashboard: https://dashboard.render.com/")
            
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")
