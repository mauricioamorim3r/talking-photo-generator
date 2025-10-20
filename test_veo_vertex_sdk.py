"""
Teste completo do Google Veo 3.1 via Vertex AI SDK
Verifica se a integração com API Key está funcionando
"""

import sys
import os
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("🎬 TESTE: Google Veo 3.1 via Vertex AI SDK")
print("=" * 80)

# 1. Verificar variáveis de ambiente
print("\n📋 1. Verificando configuração do ambiente...")
from dotenv import load_dotenv

# Carrega .env do backend
env_path = backend_path / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GOOGLE_VERTEX_API_KEY")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "talking-photo-gen-441622")  # Valor padrão
region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

print(f"   ✓ API Key: {'✅ Configurada' if api_key else '❌ NÃO ENCONTRADA'}")
print(f"   ✓ Project ID: {project_id}")
print(f"   ✓ Region: {region}")

if not api_key:
    print("\n❌ ERRO: GOOGLE_VERTEX_API_KEY não encontrada no backend/.env")
    sys.exit(1)

# 2. Verificar imports necessários
print("\n📦 2. Verificando importações...")
try:
    import requests
    print("   ✅ requests instalado")
except ImportError:
    print("   ❌ requests não encontrado")
    sys.exit(1)

# 3. Testar importação do veo31_simple
print("\n🔧 3. Testando importação do módulo veo31_simple...")
try:
    from veo31_simple import generate_video_veo31
    print("   ✅ Módulo veo31_simple importado com sucesso")
except Exception as e:
    print(f"   ❌ ERRO ao importar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Testar geração de vídeo
print("\n🎥 4. Preparando imagem de teste...")
# Cria uma imagem simples para teste
from PIL import Image
import tempfile

temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
img = Image.new('RGB', (512, 512), color='skyblue')
img.save(temp_image.name)
print(f"   ✅ Imagem criada: {temp_image.name}")

print("\n🎬 5. Testando geração de vídeo...")
print("   Prompt: 'A serene sunset over a calm ocean with gentle waves'")
print("   Configuração: 720p, 5 segundos")
print("\n   ⏳ Iniciando geração (pode demorar alguns minutos)...\n")

try:
    result = generate_video_veo31(
        prompt="A serene sunset over a calm ocean with gentle waves",
        duration=5,
        resolution="720p",
        api_key=api_key,
        project_id=project_id,
        location=region,
        image_url=temp_image.name  # Usa imagem de teste
    )
    
    print("\n" + "=" * 80)
    print("✅ SUCESSO! Vídeo gerado com Vertex AI REST API")
    print("=" * 80)
    print(f"\n📊 Resultado:")
    print(f"   - URL do vídeo: {result.get('video_url', 'N/A')}")
    print(f"   - Duração: {result.get('duration', 'N/A')}s")
    print(f"   - Resolução: {result.get('resolution', 'N/A')}")
    print(f"   - Status: {result.get('status', 'N/A')}")
    print(f"   - Custo: ${result.get('cost', 'N/A')}")
    
    if result.get('video_url'):
        print(f"\n🎬 Vídeo disponível em: {result['video_url']}")
    
    print("\n✅ Integração com Vertex AI REST API funcionando perfeitamente!")
    
    # Limpa arquivo temporário
    import os
    os.unlink(temp_image.name)
    
except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERRO durante geração")
    print("=" * 80)
    print(f"\nErro: {str(e)}\n")
    import traceback
    traceback.print_exc()
    
    # Limpa arquivo temporário
    import os
    try:
        os.unlink(temp_image.name)
    except:
        pass
    
    # Verifica tipo de erro
    if "401" in str(e) or "authentication" in str(e).lower():
        print("\n💡 DICA: Erro de autenticação")
        print("   - Verifique se GOOGLE_VERTEX_API_KEY está correto")
        print("   - Confirme se o projeto está ativo no Google Cloud")
    elif "403" in str(e) or "permission" in str(e).lower():
        print("\n💡 DICA: Erro de permissão")
        print("   - Verifique se Vertex AI API está habilitada no projeto")
        print("   - Confirme se a API Key tem permissões corretas")
    elif "404" in str(e):
        print("\n💡 DICA: Endpoint não encontrado")
        print("   - Verifique se o modelo 'veo-3.1' está disponível na região us-central1")
        print("   - Tente região diferente: europe-west4")
    
    sys.exit(1)

print("\n" + "=" * 80)
print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
print("=" * 80)
