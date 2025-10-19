import time
import requests

print('🔥 Acordando o backend...')
for i in range(3):
    response = requests.get('https://gerador-fantasia.onrender.com/health')
    print(f'  Tentativa {i+1}: {response.status_code}')
    time.sleep(1)

print('\n🎯 Testando rota de vozes...')
response = requests.get('https://gerador-fantasia.onrender.com/api/audio/voices')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'✅ {len(data.get("voices", []))} vozes disponíveis')
    
print('\n💡 Agora recarregue a página do frontend!')
print('   URL: https://foto-video-fantasia.onrender.com')
