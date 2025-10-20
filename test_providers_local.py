"""
Teste Local - Video Providers
Testa os providers de vídeo disponíveis sem fazer geração real
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from video_providers import video_manager, VideoProvider

print("🎬 TESTANDO VIDEO PROVIDERS\n")
print("=" * 60)

# 1. Listar providers disponíveis
print("\n📋 Providers Disponíveis:")
providers = video_manager.get_available_providers()

for provider, available in providers.items():
    status = "✅ Disponível" if available else "❌ Não configurado"
    print(f"  - {provider}: {status}")

# 2. Mostrar custos estimados
print("\n💰 Custos Estimados (8 segundos):")
print("-" * 60)

test_providers = [
    (VideoProvider.FAL_VEO3, "FAL.AI Veo 3.1"),
    (VideoProvider.FAL_SORA2, "FAL.AI Sora 2"),
    (VideoProvider.GOOGLE_VEO3_DIRECT, "Google Veo 3.1 Direct")
]

for provider, name in test_providers:
    if providers.get(provider):
        cost_no_audio = video_manager.estimate_cost(provider, 8, with_audio=False)
        cost_with_audio = video_manager.estimate_cost(provider, 8, with_audio=True)
        print(f"  {name}:")
        print(f"    - Sem áudio: ${cost_no_audio:.2f}")
        print(f"    - Com áudio: ${cost_with_audio:.2f}")

# 3. Comparação de economia
print("\n💸 Economia (Google vs FAL.AI):")
print("-" * 60)

if providers.get(VideoProvider.FAL_VEO3) and providers.get(VideoProvider.GOOGLE_VEO3_DIRECT):
    fal_cost = video_manager.estimate_cost(VideoProvider.FAL_VEO3, 8, with_audio=True)
    google_cost = video_manager.estimate_cost(VideoProvider.GOOGLE_VEO3_DIRECT, 8, with_audio=True)
    savings = fal_cost - google_cost
    savings_pct = (savings / fal_cost) * 100
    
    print(f"  FAL.AI:  ${fal_cost:.2f} / vídeo 8s")
    print(f"  Google:  ${google_cost:.2f} / vídeo 8s")
    print(f"  Economia: ${savings:.2f} ({savings_pct:.0f}%)")
    print(f"\n  📊 Em 100 vídeos/mês:")
    print(f"     FAL.AI:  ${fal_cost * 100:.2f}")
    print(f"     Google:  ${google_cost * 100:.2f}")
    print(f"     Economia: ${savings * 100:.2f}/mês")
else:
    print("  ⚠️ Configure ambos providers para ver comparação")

# 4. Guia de configuração
print("\n⚙️ Configuração Necessária:")
print("-" * 60)

if not providers.get(VideoProvider.FAL_VEO3):
    print("\n❌ FAL.AI não configurado:")
    print("   1. Obter chave: https://fal.ai/dashboard")
    print("   2. Adicionar ao .env: FAL_KEY=sua_chave")

if not providers.get(VideoProvider.GOOGLE_VEO3_DIRECT):
    print("\n❌ Google Veo Direct não configurado:")
    print("   1. Criar projeto: https://console.cloud.google.com")
    print("   2. Ativar Vertex AI API")
    print("   3. Criar Service Account (role: Vertex AI User)")
    print("   4. Download JSON key para ./backend/veo-service-account.json")
    print("   5. Adicionar ao .env:")
    print("      GOOGLE_CLOUD_PROJECT_ID=seu-projeto-id")
    print("      GOOGLE_APPLICATION_CREDENTIALS=./backend/veo-service-account.json")

print("\n" + "=" * 60)
print("✅ Teste concluído!\n")
