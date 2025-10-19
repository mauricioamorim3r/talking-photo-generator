#!/usr/bin/env python3
"""
Script para obter os logs do último deploy falho
"""
import requests
import json

API_KEY = "rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S"
SERVICE_ID = "srv-d3q9r8odl3ps73bp1p8g"
DEPLOY_ID = "dep-d3q9soripnbc73ad89tg"

headers = {"Authorization": f"Bearer {API_KEY}"}

print("🔍 Buscando logs do deploy falho...\n")

# Obter logs do deploy
url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys/{DEPLOY_ID}/logs"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    logs = response.json()
    
    print("=" * 70)
    print("📋 LOGS DO DEPLOY (últimas 50 linhas)")
    print("=" * 70)
    print()
    
    # Logs vêm como array de objetos
    if isinstance(logs, list):
        # Pegar as últimas 50 entradas
        recent_logs = logs[-50:] if len(logs) > 50 else logs
        
        for log_entry in recent_logs:
            timestamp = log_entry.get("timestamp", "")
            message = log_entry.get("message", "")
            print(f"{message}")
    else:
        print(logs)
    
    print()
    print("=" * 70)
else:
    print(f"❌ Erro ao obter logs: {response.status_code}")
    print(response.text)

print("\n💡 PRÓXIMOS PASSOS:")
print("1. Vá ao Dashboard: https://dashboard.render.com/static/srv-d3q9r8odl3ps73bp1p8g")
print("2. Clique em 'Settings'")
print("3. Configure:")
print("   - Build Command: npm install --legacy-peer-deps && npm run build")
print("   - Publish Directory: build")
print("4. Clique em 'Save Changes'")
print("5. Clique em 'Manual Deploy' → 'Deploy latest commit'")
