import requests

API_KEY = 'rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S'
SERVICE_ID = 'srv-d3qd08ali9vc73c8a5f0'  # Frontend service

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

print("🚀 Iniciando deploy do frontend...")
response = requests.post(
    f'https://api.render.com/v1/services/{SERVICE_ID}/deploys',
    headers=headers,
    json={}
)

if response.status_code == 201:
    data = response.json()
    print(f"✅ Deploy iniciado com sucesso!")
    print(f"📝 Deploy ID: {data['id']}")
    print(f"🔗 Dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
else:
    print(f"❌ Erro: {response.status_code}")
    print(f"Response: {response.text}")
