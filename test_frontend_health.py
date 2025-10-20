"""Test frontend service health"""
import requests
import time

URL = "https://foto-video-fantasias.onrender.com"

print("🔍 Testando serviço frontend...\n")

# Test 1: Basic connectivity
print("1️⃣ Teste de conectividade básica")
try:
    response = requests.get(URL, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 502:
        print(f"\n❌ 502 Bad Gateway - Serviço não está respondendo")
        print(f"   Possíveis causas:")
        print(f"   • Start command incorreto")
        print(f"   • Porta não configurada corretamente")
        print(f"   • Serve não instalado")
        print(f"   • Serviço crashando ao iniciar")
    elif response.status_code == 200:
        print(f"\n✅ Serviço respondendo!")
        if 'id="root"' in response.text:
            print(f"   ✅ React app carregada")
        else:
            print(f"   ⚠️  React app não encontrada")
            
except requests.exceptions.Timeout:
    print(f"   ⏱️  Timeout - Serviço não responde")
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ Erro de conexão: {e}")

# Test 2: Health check
print(f"\n2️⃣ Teste de health check")
try:
    response = requests.get(f"{URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Health check falhou: {type(e).__name__}")

print(f"\n📋 Próximos passos:")
print(f"   1. Verifique os logs no dashboard do Render")
print(f"   2. Confirme que o Start Command é: serve -s build -l $PORT")
print(f"   3. Confirme que o Build Command inclui: npm install -g serve")
print(f"   4. Faça Manual Deploy → Clear build cache & deploy")
