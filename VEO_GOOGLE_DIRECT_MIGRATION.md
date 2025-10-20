# 🎯 Migração: Veo 3.1 via Google Direto (sem FAL.AI)

## 💰 Economia de Custos

| Item | FAL.AI (Atual) | Google Direto | Economia |
|------|----------------|---------------|----------|
| Veo 3.1 com áudio | $0.40/seg | ~$0.15/seg | 62% |
| Veo 3.1 sem áudio | $0.20/seg | ~$0.12/seg | 40% |
| Vídeo 8s com áudio | $3.20 | ~$1.20 | 62% |
| 100 vídeos/mês | $320 | ~$120 | **$200/mês** |

## ✅ Vantagens

1. **Custo menor** - 40-62% de economia
2. **Controle direto** - Sem intermediários
3. **Mesma qualidade** - Mesmo modelo Veo 3.1
4. **Prioridade** - Acesso direto ao Google
5. **Customização** - Mais parâmetros disponíveis

## 📋 Requirements

### 1. Criar Projeto no Google Cloud

```bash
# Acesse: https://console.cloud.google.com
# Crie novo projeto: "talking-photo-generator"
# Anote o Project ID
```

### 2. Ativar APIs

```bash
# No Google Cloud Console:
# APIs & Services → Enable APIs
# Ative:
- Vertex AI API
- Cloud Storage API
- IAM API
```

### 3. Criar Service Account

```bash
# IAM & Admin → Service Accounts → Create
Nome: veo-video-generator
Role: Vertex AI User + Storage Object Viewer

# Criar chave JSON:
# Actions → Manage Keys → Add Key → JSON
# Download: veo-service-account.json
```

### 4. Instalar Dependências

```bash
pip install google-cloud-aiplatform google-auth google-auth-httplib2
```

## 🔧 Implementação

### Adicionar ao requirements.txt

```txt
google-cloud-aiplatform>=1.38.0
google-auth>=2.25.0
google-auth-httplib2>=0.2.0
```

### Adicionar Environment Variables no Render

```bash
GOOGLE_CLOUD_PROJECT_ID=seu-project-id
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/veo-service-account.json
USE_GOOGLE_VEO_DIRECT=true  # Flag para ativar
```

### Fazer Upload da Service Account Key

**Render Dashboard → Environment → Secret Files:**
```
File Name: veo-service-account.json
Contents: [cole o conteúdo do arquivo JSON]
```

## 🚀 Código de Migração

### 1. Atualizar server.py

```python
# Adicionar no início
from backend.veo31_direct import Veo31DirectAPI, generate_video_veo31_direct

# Atualizar endpoint /video/generate
@api_router.post("/video/generate")
async def generate_video(request: GenerateVideoRequest):
    if request.mode == "premium" and request.model == "veo3":
        
        # Verificar se deve usar Google direto
        use_google_direct = os.getenv("USE_GOOGLE_VEO_DIRECT", "false") == "true"
        
        if use_google_direct:
            # NOVO: Via Google Vertex AI
            result = await generate_video_veo31_direct(
                image_url=request.image_url,
                prompt=request.prompt,
                duration=8,
                with_audio=True
            )
            result_url = result['video_url']
            actual_cost = result['cost']
            provider = "google-vertex-ai"
        else:
            # ANTIGO: Via FAL.AI
            handler = fal_client.submit(
                "fal-ai/veo3.1/image-to-video",
                arguments={
                    "image_url": request.image_url,
                    "prompt": request.prompt,
                    "duration": "8s"
                }
            )
            result = await asyncio.get_event_loop().run_in_executor(
                None, handler.get
            )
            result_url = result.get('video', {}).get('url')
            actual_cost = 8 * 0.40
            provider = "fal-ai"
        
        # Salvar no banco com custo real
        video = VideoGeneration(
            video_id=video_id,
            image_id=request.image_id,
            model=request.model,
            prompt=request.prompt,
            duration=8,
            cost=actual_cost,
            provider=provider,
            status="completed",
            result_url=result_url
        )
        
        return {
            "success": True,
            "video_url": result_url,
            "cost": actual_cost,
            "provider": provider,
            "savings": f"${(3.20 - actual_cost):.2f}" if use_google_direct else "N/A"
        }
```

### 2. Atualizar estimativa de custos

```python
@api_router.post("/video/estimate-cost")
async def estimate_cost(request: EstimateCostRequest):
    if request.model == "veo3":
        use_google_direct = os.getenv("USE_GOOGLE_VEO_DIRECT", "false") == "true"
        
        if use_google_direct:
            # Google pricing
            base_cost = 0.12  # ~$0.12/seg
            audio_cost = 0.03 if request.with_audio else 0
            cost = request.duration * (base_cost + audio_cost)
        else:
            # FAL.AI pricing
            cost = request.duration * (0.40 if request.with_audio else 0.20)
        
        return {
            "estimated_cost": cost,
            "provider": "google-vertex-ai" if use_google_direct else "fal-ai"
        }
```

## 🧪 Testes

### 1. Testar localmente

```bash
# Configurar credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/veo-service-account.json"
export GOOGLE_CLOUD_PROJECT_ID="seu-project-id"
export USE_GOOGLE_VEO_DIRECT="true"

# Testar
python test_veo_direct.py
```

### 2. Script de teste

```python
# test_veo_direct.py
import asyncio
from backend.veo31_direct import generate_video_veo31_direct

async def test():
    result = await generate_video_veo31_direct(
        image_url="https://example.com/image.jpg",
        prompt="A cat looking curious, blinking slowly",
        duration=8,
        with_audio=True
    )
    
    print(f"✅ Video gerado: {result['video_url']}")
    print(f"💰 Custo: ${result['cost']}")
    print(f"⏱️ Duração: {result['duration']}s")

asyncio.run(test())
```

## 📊 Migração Gradual

### Fase 1: Teste (Semana 1)
```bash
# Manter FAL.AI como padrão
USE_GOOGLE_VEO_DIRECT=false

# Testar Google em 10% dos requests
# (implementar feature flag)
```

### Fase 2: A/B Test (Semana 2-3)
```bash
# 50% FAL.AI, 50% Google
# Comparar qualidade e custos
```

### Fase 3: Migração Total (Semana 4)
```bash
# 100% Google Vertex AI
USE_GOOGLE_VEO_DIRECT=true

# Remover dependência fal-client do veo3
```

## 💾 Schema do Banco de Dados

Adicionar campo `provider` na tabela:

```sql
ALTER TABLE video_generations 
ADD COLUMN provider VARCHAR(50) DEFAULT 'fal-ai';

-- Valores possíveis: 'fal-ai', 'google-vertex-ai'
```

## 🔍 Monitoramento

### Métricas para acompanhar:

1. **Custo por vídeo**
   - FAL.AI: ~$3.20
   - Google: ~$1.20
   - Target: <$1.50

2. **Tempo de geração**
   - FAL.AI: ~30-45s
   - Google: ~20-35s (esperado)

3. **Taxa de sucesso**
   - Target: >95%

4. **Qualidade percebida**
   - User feedback
   - Video quality metrics

## ⚠️ Considerações

### Limitações do Google Veo

1. **Quotas**
   - Free tier: Limitado
   - Paid: Conforme projeto
   - Monitorar usage

2. **Regions**
   - Disponível em: us-central1, europe-west4
   - Escolher mais próximo

3. **Pricing**
   - Verificar pricing oficial do Google
   - Valores aqui são estimativas
   - Pode variar por região

### Fallback Strategy

Se Google falhar, usar FAL.AI:

```python
try:
    result = await generate_video_veo31_direct(...)
except Exception as e:
    logger.warning(f"Google Veo failed, fallback to FAL.AI: {e}")
    # Use FAL.AI
    result = fal_client.submit("fal-ai/veo3.1/image-to-video", ...)
```

## 📝 Checklist de Deploy

- [ ] Criar projeto no Google Cloud
- [ ] Ativar Vertex AI API
- [ ] Criar service account
- [ ] Fazer download da chave JSON
- [ ] Adicionar chave como Secret File no Render
- [ ] Adicionar env vars no Render
- [ ] Instalar dependências (`pip install google-cloud-aiplatform`)
- [ ] Atualizar `requirements.txt`
- [ ] Implementar código no `server.py`
- [ ] Testar localmente
- [ ] Deploy no Render
- [ ] Testar em produção
- [ ] Monitorar custos
- [ ] Ajustar quotas se necessário

## 🎯 Resultado Esperado

**Economia mensal (100 vídeos):**
```
FAL.AI:        100 vídeos × $3.20 = $320/mês
Google Direto: 100 vídeos × $1.20 = $120/mês
-------------------------------------------
ECONOMIA:                          $200/mês
ECONOMIA ANUAL:                  $2,400/ano
```

## 📞 Próximos Passos

1. Criar conta no Google Cloud
2. Configurar projeto e APIs
3. Testar implementação localmente
4. Deploy gradual em produção
5. Monitorar e ajustar

Quer que eu ajude com algum desses passos? 🚀
