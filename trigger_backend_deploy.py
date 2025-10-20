import requests

API_KEY = 'rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S'
SERVICE_ID = 'srv-d3q80d0gjchc73b48p40'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

print("🚀 Iniciando deploy do backend...")
response = requests.post(
    f'https://api.render.com/v1/services/{SERVICE_ID}/deploys',
    headers=headers,
    json={}
)

if response.status_code == 201:
    deploy_id = response.json().get('id', 'N/A')
    print(f"✅ Deploy iniciado com sucesso!")
    print(f"📝 Deploy ID: {deploy_id}")
    print(f"🔗 Dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
else:
    print(f"❌ Erro {response.status_code}")
    print(f"📄 Resposta: {response.text}")
