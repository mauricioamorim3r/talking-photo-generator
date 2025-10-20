from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone
import fal_client
from elevenlabs import ElevenLabs
from emergent_wrapper import LlmChat, UserMessage, FileContentWithMimeType
import base64
import io
from PIL import Image
from gradio_client import Client
from database import db as database

# Import video providers manager
from video_providers import video_manager, VideoProvider

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure APIs
fal_key = os.environ.get('FAL_KEY', '')
os.environ['FAL_KEY'] = fal_key

elevenlabs_client = ElevenLabs(api_key=os.environ.get('ELEVENLABS_KEY', ''))

# Backend URL for serving images
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class ImageAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_url: str
    cloudinary_id: Optional[str] = None
    analysis: str
    suggested_model: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AudioGeneration(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audio_url: str
    source: Literal["generated", "uploaded"]
    duration: Optional[float] = None
    text: Optional[str] = None
    voice_id: Optional[str] = None
    voice_settings: Optional[dict] = None
    cost: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VideoGeneration(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_id: str
    audio_id: Optional[str] = None
    model: Literal["veo3", "sora2", "wav2lip", "open-sora", "wav2lip-free", "google_veo3"]
    provider: Optional[Literal["fal", "google"]] = "fal"  # Novo: provider separado
    mode: Literal["premium", "economico"] = "premium"
    prompt: str
    duration: Optional[float] = None
    cost: float = 0.0
    estimated_cost: float = 0.0
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    result_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TokenUsage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service: str
    operation: str
    cost: float
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== REQUEST/RESPONSE MODELS ====================

class AnalyzeImageRequest(BaseModel):
    image_url: Optional[str] = None  # For backward compatibility
    image_data: Optional[str] = None  # Base64 image data

class GenerateAudioRequest(BaseModel):
    text: str
    voice_id: str = "cgSgspJ2msm6clMCkdW9"  # Default child voice
    stability: float = 0.5
    similarity_boost: float = 0.75
    speed: float = 1.0
    style: float = 0.0

class GenerateVideoRequest(BaseModel):
    image_url: str
    model: Literal["veo3", "sora2", "wav2lip", "open-sora", "wav2lip-free", "google_veo3"]
    provider: Optional[Literal["fal", "google"]] = "fal"  # Novo: escolha de provider
    mode: Literal["premium", "economico"] = "premium"
    prompt: str
    audio_url: Optional[str] = None
    duration: Optional[int] = 5
    cinematic_settings: Optional[dict] = None

class EstimateCostRequest(BaseModel):
    model: Literal["veo3", "sora2", "wav2lip", "open-sora", "wav2lip-free", "google_veo3"]
    provider: Optional[Literal["fal", "google"]] = "fal"  # Novo
    mode: Literal["premium", "economico"] = "premium"
    duration: int
    with_audio: bool = False

class GeneratedImage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str
    image_url: str
    cost: float = 0.039  # Nano Banana cost per image
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GenerateImageRequest(BaseModel):
    prompt: str

class VerifyPasswordRequest(BaseModel):
    password: str

class TokenUsageStats(BaseModel):
    total_spent: float
    by_service: dict
    recent_operations: List[TokenUsage]

class APIBalance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service: str
    initial_balance: float
    current_balance: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UpdateBalanceRequest(BaseModel):
    service: str
    initial_balance: float

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Video Generation API"}

class ImageUploadRequest(BaseModel):
    """Request body for base64 image upload"""
    image_data: str  # Base64 encoded image with data:image prefix

@api_router.post("/images/upload")
async def upload_image(request: ImageUploadRequest):
    """Accept base64 image directly (no external storage needed)"""
    try:
        # Validate base64 format
        if not request.image_data.startswith('data:image'):
            raise HTTPException(status_code=400, detail="Invalid base64 format. Must start with 'data:image'")
        
        # Extract base64 data
        base64_data = request.image_data.split(',')[1] if ',' in request.image_data else request.image_data
        
        # Validate by decoding
        image_bytes = base64.b64decode(base64_data)
        
        # Optional: Validate it's a valid image using PIL
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        
        logger.info(f"✅ Image uploaded successfully - Format: {img.format}, Size: {len(image_bytes)} bytes")
        
        return {
            "success": True,
            "image_data": request.image_data,  # Return base64 to use directly
            "format": img.format,
            "size_bytes": len(image_bytes)
        }
    except Exception as e:
        logger.error(f"Error processing image upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/images/analyze")
async def analyze_image(request: AnalyzeImageRequest):
    """Analyze image with Gemini and suggest best model with cinematic prompts"""
    try:
        # Handle Base64 image data or URL
        if request.image_data:
            # Extract base64 data
            base64_data = request.image_data
            if ',' in base64_data:
                base64_data = base64_data.split(',', 1)[1]
            
            # Decode base64 to bytes
            img_data = base64.b64decode(base64_data)
            logger.info(f"📎 Analyzing image from Base64 (size: {len(img_data)} bytes)")
        elif request.image_url:
            # Download from URL (legacy support)
            import requests
            img_response = requests.get(request.image_url)
            img_data = img_response.content
            logger.info(f"📎 Analyzing image from URL: {request.image_url}")
        else:
            raise HTTPException(status_code=400, detail="Either image_data or image_url must be provided")

        # Save temporarily for Gemini
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}.jpg")
        with open(temp_path, 'wb') as f:
            f.write(img_data)
        
        # Analyze with Gemini
        chat = LlmChat(
            api_key=os.environ.get('GEMINI_KEY', ''),
            session_id=str(uuid.uuid4()),
            system_message="""Você é um diretor de fotografia especialista em criar prompts cinematográficos otimizados para Veo 3.1 e Sora 2.

**🚨 POLÍTICA DE CONTEÚDO CRÍTICA - ANTI-DEEPFAKE 🚨**
NUNCA mencione ou inclua QUALQUER referência a:
- ❌ "manter identidade facial", "preservar características faciais", "fidelidade facial", "não alterar rosto"
- ❌ "100% da identidade", "expressões faciais devem ser preservadas", "características originais"
- ❌ "alta fidelidade", "exatamente como na foto", "sem modificar o rosto"
- ❌ "semelhança exata", "identidade visual preservada", "características físicas mantidas"

**IMPORTANTE:** Os modelos Veo 3.1 e Sora 2 JÁ mantêm automaticamente a imagem original como base.
Você deve descrever APENAS o MOVIMENTO, AÇÃO e CINEMATOGRAFIA desejados.

**RESTRIÇÕES DE SEGURANÇA - O QUE NUNCA INCLUIR:**

1. **Violência Gráfica/Sofrimento:**
   ❌ ferimento, sangue, mutilação, dor extrema, tortura, morte
   ✅ USE: tensão cinematográfica, personagens com emoção intensa, perigo fictício

2. **Conteúdo Sexual/Explícito:**
   ❌ nudez, atos sexuais, conteúdo sugestivo adulto
   ✅ USE: retrato artístico, fotografia comercial elegante

3. **Desinformação/Deepfakes:**
   ❌ figuras públicas reais dizendo/fazendo coisas não autênticas
   ❌ eventos de notícias falsas ou enganosas
   ✅ USE: personagens fictícios, cenários claramente artísticos

4. **Discurso de Ódio/Discriminação:**
   ❌ estereótipos nocivos, conteúdo discriminatório
   ✅ USE: representação respeitosa e inclusiva

5. **Atividades Ilegais/Perigosas:**
   ❌ drogas, automutilação, armas perigosas, atos criminosos
   ✅ USE: atividades seguras e legais

**PALAVRAS PROIBIDAS E SUBSTITUIÇÕES:**
❌ ameaçador → ✅ impressionante, majestoso
❌ violento → ✅ intenso, dramático
❌ ataque/atacar → ✅ aproximação, se aproximar
❌ sangue → ✅ efeito visual dramático
❌ armas → ✅ objetos cênicos (se contextualmente apropriado)
❌ terror/pânico → ✅ impacto, admiração, surpresa
❌ agressivo → ✅ energético, vigoroso
❌ afiado → ✅ visível, definido
❌ medo extremo → ✅ emoção intensa, reação dramática

**⚠️ CONTEÚDO SENSÍVEL COM CRIANÇAS:**
Quando a imagem contiver CRIANÇAS (menores de 18 anos):
- ✅ PERMITIDO: "criança sorrindo", "brincando", "correndo", "acenando", "olhando curiosamente"
- ❌ EVITE: ações com comida/bebida na boca, close-ups extremos do rosto
- ❌ EVITE: descrições faciais detalhadas excessivas
- ✅ FOQUE: wide shots ou medium shots, ações lúdicas e seguras
- ✅ USE: descrições gerais e neutras

---

## 📽️ TEMPLATE ESPECÍFICO PARA VEO 3.1

**Quando usar**: Produção cinematográfica de alta qualidade, áudio sincronizado complexo, realismo de movimento extremo

**Estrutura do Prompt para Veo 3.1 (Profissional - 7 Camadas):**
```
1. [AÇÃO PRINCIPAL]: movimento detalhado e específico do sujeito, timing, transições naturais
2. [CINEMATIC SHOT]: tipo de plano profissional + movimento de câmera técnico
3. [LENTE E FOCO]: especificações exatas (focal length, aperture, depth of field, bokeh)
4. [LIGHTING DESIGN]: setup de iluminação profissional (key, fill, rim, bounce, temperatura de cor)
5. [COLOR GRADING]: paleta cinematográfica específica, mood, look references (filme comercial, documentário, etc.)
6. [INSTRUÇÃO DE ÁUDIO]: ESSENCIAL para sincronização - descreva camadas de som (diálogo/fala, foley, ambiente, música)
7. [QUALIDADE & EXCLUSÕES]: hyper-realistic, resolução 4K/8K, estilo de filmagem + sem distrações visuais
```

**INSTRUÇÃO DE ÁUDIO para Veo 3.1 (ESSENCIAL):**
Sempre inclua uma seção explícita de áudio seguindo este formato:
"Instrução de Áudio: O vídeo deve incluir áudio sincronizado com [descrição da ação]. [Detalhes do áudio: voz/som principal, sons ambiente, música de fundo, efeitos sonoros]. Volume e mixagem: [prioridades de áudio]."

**Exemplo Veo 3.1 Completo:**
"Homem de meia-idade virando a cabeça lentamente da esquerda para a direita em 3 segundos, sorriso autêntico surgindo gradualmente, olhos brilhando com luz refletida natural, cabelo movendo-se sutilmente com o movimento, micro-expressões faciais realistas (pestanejar, leve franzir de sobrancelhas). Close-up cinematográfico profissional, câmera estática montada em tripod com gimbal, rack focus suave transicionando do fundo desfocado (bokeh cremoso) para o rosto em foco nítido. Shot com lente prime 85mm f/1.4, abertura ampla criando shallow depth of field pronunciado, bokeh hexagonal característico no background desfocado. Three-point lighting setup premium: key light LED suave COB de 45° direita criando sombras naturais e profundidade facial, fill light difuso LED panel esquerda reduzindo contraste a 40%, rim light backlight dourado 135° destacando contorno do cabelo e ombro com halo sutil separando do fundo. Color grading cinematográfico de comercial premium: tons quentes (amber 3200K) nas highlights da pele, teal sutil nos mid-tones, shadows com leve crush para look filmic, contraste médio-alto, saturação controlada 85%, look de filme publicitário high-end. Instrução de Áudio: O vídeo deve incluir áudio sincronizado com o movimento da cabeça. Som ambiente corporativo suave de escritório moderno a 15% (teclados distantes, conversas baixas), respiração natural do homem quase imperceptível, leve som de movimento de roupa, música instrumental inspiradora de piano e cordas ao fundo a 25%, tudo mixado com foco na presença natural. Hyper-realistic 4K ProRes, textura de pele ultra-detalhada com poros e linhas naturais visíveis, cabelo com definição strand-by-strand, filmado em estilo de luxury brand commercial production. Sem watermarks, sem lower thirds, sem lens flares artificiais excessivos, color grading consistente frame-by-frame."

---

## 📽️ TEMPLATE ESPECÍFICO PARA SORA 2

**Quando usar**: Cenas com física realista, movimento de personagens, ambientes detalhados, geração de áudio nativo

**Estrutura do Prompt para Sora 2 (7 Camadas):**
```
1. [CENA E AMBIENTE]: descrição do ambiente, hora do dia, condições climáticas, atmosfera geral
2. [SUJEITO E AÇÃO]: quem/o que está na cena, movimento principal, emoções, ritmo da ação
3. [PHYSICS & MATERIALS]: texturas físicas, interações naturais, comportamento de materiais (tecido, pelo, água, folhas, poeira)
4. [CINEMATOGRAFIA]: tipo de plano (close-up, medium, wide), movimento de câmera, lente, framing
5. [ILUMINAÇÃO E COR]: fontes de luz naturais/artificiais, direção, mood, paleta de cores específica
6. [INSTRUÇÃO DE ÁUDIO]: sons naturais da cena (Sora 2 gera áudio nativo) - fala, passos, vento, água, etc.
7. [QUALIDADE + EXCLUSÕES]: resolução desejada, estilo visual, texturas + elementos a evitar (watermarks/artifacts)
```

**INSTRUÇÃO DE ÁUDIO para Sora 2 (ESSENCIAL):**
Sora 2 gera áudio NATIVO da cena. Sempre descreva:
"Instrução de Áudio: O vídeo deve incluir áudio naturalista com [sons principais da ação], [sons ambiente do cenário], [sons secundários de interação física]. [Opcional: música de fundo ou atmosfera sonora]."

**Exemplo Sora 2 Completo:**
"Campo de flores silvestres coloridas ao amanhecer, névoa leve dissipando-se sobre o solo, atmosfera serena e mágica com luz dourada do sol nascente. Golden retriever de pelo médio correndo com energia natural e alegria, orelhas balançando ritmicamente ao vento, língua para fora em expressão feliz, patas tocando o solo com movimento cadenciado, cauda abanando vigorosamente. Física realista cinematográfica: pelo texturizado e volumoso movendo-se com física natural do vento, flores silvestres balançando suavemente em ondas sincronizadas, gotas de orvalho visíveis nas pétalas refletindo luz do sol, partículas de pólen suspensas no ar com movimento lento. Medium shot inicial transitando suavemente para wide shot revelando paisagem, câmera acompanha o movimento lateral do cachorro com dolly tracking suave e fluido, movimento estabilizado. Lente 50mm f/2.8 com shallow depth of field moderado, foco principal no cachorro com fundo levemente desfocado (bokeh suave), framing seguindo regra dos terços. Iluminação golden hour natural: luz quente e difusa lateral direita 60°, raios de sol filtrados através das flores criando god rays e lens flare natural orgânico, sombras longas e suaves projetadas no chão, highlights dourados no pelo do cachorro. Paleta de cores vibrante: tons âmbar e dourados dominantes, verdes saturados da vegetação, azuis sutis no céu, contraste médio-baixo para mood calmo. Instrução de Áudio: O vídeo deve incluir áudio naturalista com sons rítmicos e claros das quatro patas do cachorro tocando a grama, respiração energética e ofegante do animal, vento suave rustling nas flores e folhagens, pássaros cantando melodiosamente ao fundo, sons de insetos matinais sutis. Filmado em estilo de documentário de natureza em 35mm film stock, cinematic color grading orgânico, 4K UHD, texturas ultra-detalhadas de pelo animal e vegetação. Sem watermarks, sem text overlays, sem artifacts digitais ou compression, sem cores irrealistas."

---

## 🎬 TEMPLATES SIMPLIFICADOS (Modelos Econômicos)

**Para Open-Sora (gratuito):**
"[Sujeito] fazendo [ação específica]. [Tipo de plano: close/medium/wide]. [Iluminação básica: natural/suave/dramática]. [Movimento: natural/suave/energético]. Qualidade cinematográfica."

**Para Wav2lip (sincronização labial):**
"[Pessoa] falando [tipo de fala: calmamente/animadamente] diretamente para a câmera. Close-up. Boa iluminação frontal difusa. Movimento labial sincronizado com áudio. HD quality."

---

## 📋 FORMATO DE RESPOSTA JSON

Retorne EXATAMENTE este JSON:
{
  "description": "Descrição detalhada do que você vê na imagem",
  "subject_type": "pessoa/animal/objeto/boneco/criatura",
  "has_face": true ou false,
  "composition": "Análise da composição atual da imagem",
  "recommended_model_premium": "sora2" ou "veo3" ou "wav2lip",
  "recommended_model_economico": "open-sora" ou "wav2lip-free",
  "reason_premium": "Justificativa técnica da escolha (mencione o modelo específico)",
  "reason_economico": "Justificativa da opção gratuita",
  "prompt_sora2": "Prompt COMPLETO seguindo o template Sora 2 - SEM menções a identidade facial",
  "prompt_veo3": "Prompt COMPLETO seguindo o template Veo 3 - SEM menções a identidade facial",
  "prompt_economico": "Prompt simplificado para modelos gratuitos",
  "cinematic_details": {
    "subject_action": "Descrição detalhada da ação",
    "camera_work": "Plano e movimento de câmera",
    "lighting": "Setup de iluminação",
    "audio_design": "Design de áudio (para modelos premium)",
    "style": "Estilo visual e qualidade"
  },
  "tips": "Dicas para melhor resultado"
}

---

## ✅ EXEMPLO COM CRIANÇA (CONTEÚDO SENSÍVEL):

❌ **ERRADO:** "Criança levando colher à boca, café derretendo na boca, close-up extremo do rosto..."

✅ **CORRETO:**
```json
{
  "prompt_sora2": "Criança sorrindo e brincando em um ambiente seguro e familiar. Medium shot com câmera estável. Iluminação natural suave. Color grading quente e acolhedor. Áudio: sons de risadas e ambiente alegre. Filmado em estilo documental de família, 4K.",
  
  "prompt_veo3": "Criança em atividade lúdica natural, sorrindo espontaneamente. Wide shot cinematográfico mantendo distância respeitosa. Soft lighting natural. Color grading: tons quentes familiares. Audio design: ambiente doméstico agradável, risadas naturais. Shot em estilo de fotografia de família profissional."
}
```

## ✅ EXEMPLO COMPLETO CORRETO (Gato):

❌ **ERRADO:** "Gato malhado mantendo 100% da identidade facial original e preservando todas as características faciais com fidelidade..."

✅ **CORRETO:**
```json
{
  "prompt_sora2": "Gato malhado laranja levantando a cabeça lentamente, orelhas se movendo em atenção, olhos grandes focando diretamente na câmera, bigodes tremendo sutilmente. Medium shot com movimento sutil de aproximação da câmera. Lente 35mm, foco nítido no rosto. Iluminação natural suave de janela, criando soft shadows. Color grading quente e acolhedor. Áudio: ronronar suave, pequenos movimentos, som ambiente calmo de casa. Filmado em estilo documental naturalista, 4K, textura detalhada de pelo.",
  
  "prompt_veo3": "Gato sentado olhando para cima com curiosidade, pupilas dilatadas reagindo à luz, movimento sutil de pestanejar, cauda balançando levemente ao lado. Cinematic close-up com lente 50mm f/2.0, shallow depth of field isolando o sujeito. Soft key light de 45 graus, fill light natural, rim light destacando o pelo. Color grading: tons naturais com leve warmth, preservando a textura real. Audio design: ambiente de casa silencioso, respiração suave do gato, leve som de movimento, atmosfera calma. Hyper-realistic, texturas de pelo em 4K, shot em estilo de pet commercial profissional."
}
```

**LEMBRE-SE:** Os modelos automaticamente usam a imagem como base. Você só precisa descrever o MOVIMENTO e CINEMATOGRAFIA desejados."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        image_file = FileContentWithMimeType(
            file_path=temp_path,
            mime_type="image/jpeg"
        )
        
        user_message = UserMessage(
            text="Analise esta imagem como um diretor de fotografia e sugira prompts cinematográficos completos para ambos os modos (Premium e Econômico).",
            file_contents=[image_file]
        )
        
        # Add timeout to Gemini call
        import asyncio
        try:
            response = await asyncio.wait_for(
                chat.send_message(user_message),
                timeout=30.0  # 30 seconds timeout
            )
        except asyncio.TimeoutError:
            logger.error("Gemini analysis timed out")
            # Return a default analysis with new structure
            analysis_data = {
                "description": "Imagem carregada",
                "subject_type": "desconhecido",
                "has_face": False,
                "composition": "Análise não disponível - use configurações manuais",
                "recommended_model_premium": "sora2",
                "recommended_model_economico": "open-sora",
                "reason_premium": "Sora 2 oferece alta qualidade com física realista e áudio nativo",
                "reason_economico": "Open-Sora é uma opção gratuita confiável",
                "prompt_sora2": "Sujeito em movimento natural e realista, com ação suave e orgânica. Medium shot com câmera estática. Lente 50mm, foco no sujeito. Soft natural light. Color grading cinematográfico com tons naturais. Áudio: ambiente natural com sons de movimento sutis. Filmado em estilo documental, 4K, texturas detalhadas.",
                "prompt_veo3": "Movimento natural e cinematográfico do sujeito. Close-up com lente 85mm f/1.8, shallow depth of field. Three-point lighting setup profissional. Color grading com tons cinematográficos. Audio design: ambiente natural com elementos sonoros sincronizados. Hyper-realistic, 4K, estilo de commercial high-end.",
                "prompt_economico": "Animação suave e natural da imagem. Medium shot. Iluminação natural. Movimento realista. Qualidade cinematográfica.",
                "cinematic_details": {
                    "subject_action": "Movimento natural e realista do sujeito",
                    "camera_work": "Medium shot, câmera estática",
                    "lighting": "Soft natural light",
                    "audio_design": "Ambiente natural com sons sutis",
                    "style": "Cinematográfico, 4K, texturas detalhadas"
                },
                "tips": "Análise automática não disponível. Você pode editar o prompt conforme necessário para seu vídeo específico."
            }
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                "success": True,
                "analysis": analysis_data,
                "warning": "Análise automática falhou. Usando configurações padrão."
            }
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Parse response
        import json
        analysis_data = json.loads(response.strip('```json').strip('```').strip())
        
        # Function to sanitize all prompts in analysis
        def sanitize_analysis_prompts(data):
            """Clean all prompts in analysis data - Remove content policy violations"""

            # 1. VIOLÊNCIA E CONTEÚDO GRÁFICO
            violence_words = {
                'ameaçador': 'impressionante',
                'ameaçadora': 'impressionante',
                'ameaçadoramente': 'majestosamente',
                'assustador': 'surpreendente',
                'assustadora': 'surpreendente',
                'violento': 'intenso',
                'violenta': 'intensa',
                'violentamente': 'intensamente',
                'afiados': 'visíveis',
                'afiado': 'visível',
                'afiada': 'visível',
                'ataque': 'aproximação',
                'atacar': 'se aproximar',
                'atacando': 'se aproximando',
                'medo': 'admiração',
                'terror': 'impacto',
                'pânico': 'intensidade',
                'sangue': 'efeito visual dramático',
                'morte': 'drama',
                'morrer': 'desaparecer',
                'morto': 'imóvel',
                'matar': 'neutralizar',
                'agressiv': 'energétic',
                'ferimento': 'marca dramática',
                'ferido': 'afetado',
                'ferir': 'impactar',
                'tortura': 'tensão extrema',
                'mutilação': 'transformação dramática',
                'brutal': 'intenso',
                'sangrento': 'dramático',
                'arma': 'objeto cênico',
                'armas': 'objetos cênicos',
                'faca': 'objeto metálico',
                'facas': 'objetos metálicos',
                'espada': 'lâmina cênica',
                'pistola': 'objeto de cena',
                'revólver': 'objeto de cena',
            }

            # 2. CONTEÚDO SEXUAL/EXPLÍCITO (adicional)
            explicit_words = {
                'nu': 'sem adornos',
                'nua': 'natural',
                'nudez': 'naturalidade',
                'despido': 'simples',
                'sensual': 'elegante',
            }

            # 3. DEEPFAKE E IDENTIDADE (já coberto nos patterns abaixo)

            # 4. DISCURSO DE ÓDIO (prevenção)
            hate_speech_words = {
                'odiar': 'desgostar',
                'ódio': 'antipatia',
            }

            # 5. ATIVIDADES ILEGAIS
            illegal_words = {
                'droga': 'substância',
                'drogas': 'substâncias',
                'cocaína': 'pó branco',
                'maconha': 'erva',
            }

            # Combinar todos os dicionários
            problematic_words = {
                **violence_words,
                **explicit_words,
                **hate_speech_words,
                **illegal_words
            }
            
            # Clean all string fields recursively
            def clean_text(text):
                if not isinstance(text, str):
                    return text
                cleaned = text
                
                # Remove problematic words
                for word, replacement in problematic_words.items():
                    cleaned = cleaned.replace(word, replacement)
                
                # Remove facial fidelity instructions (triggers deepfake detection)
                import re
                fidelity_patterns = [
                    r'\[Manter a identidade facial.*?\]',
                    r'\[.*?NÃO DEVEM ser alterados.*?\]',
                    r'\[.*?preservando 100%.*?\]',
                    r'Manter a identidade facial.*?características físicas\.',
                    r'Os rostos.*?NÃO DEVEM.*?substituídos\.',
                    r'preservando 100% da fidelidade.*?\.'
                ]
                
                for pattern in fidelity_patterns:
                    cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
                
                # Clean up extra spaces
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                
                return cleaned
            
            def clean_dict(d):
                if isinstance(d, dict):
                    return {k: clean_dict(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [clean_dict(item) for item in d]
                elif isinstance(d, str):
                    return clean_text(d)
                return d
            
            return clean_dict(data)
        
        # Sanitize the analysis data
        analysis_data = sanitize_analysis_prompts(analysis_data)

        # Save to database (use base64 placeholder if no URL)
        image_url_for_db = request.image_url or "base64://uploaded_image"
        
        analysis = ImageAnalysis(
            image_url=image_url_for_db,
            analysis=json.dumps(analysis_data),
            suggested_model=analysis_data.get('recommended_model_premium', 'veo3')
        )

        doc = analysis.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await database.insert_image_analysis(doc)
        
        return {
            "success": True,
            "analysis": analysis_data
        }
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/audio/voices")
async def get_voices():
    """Get available ElevenLabs voices"""
    try:
        voices_response = elevenlabs_client.voices.get_all()
        
        # Filter for child voices or Portuguese
        voices = []
        for voice in voices_response.voices:
            voice_data = {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category if hasattr(voice, 'category') else "general",
                "labels": voice.labels if hasattr(voice, 'labels') else {}
            }
            voices.append(voice_data)
        
        return {"success": True, "voices": voices}
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/audio/generate")
async def generate_audio(request: GenerateAudioRequest):
    """Generate audio with ElevenLabs"""
    try:
        from elevenlabs import VoiceSettings
        
        voice_settings = VoiceSettings(
            stability=request.stability,
            similarity_boost=request.similarity_boost,
            style=request.style,
            use_speaker_boost=True
        )
        
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=request.text,
            voice_id=request.voice_id,
            model_id="eleven_multilingual_v2",
            voice_settings=voice_settings
        )
        
        # Collect audio data
        audio_data = b""
        for chunk in audio_generator:
            audio_data += chunk
        
        # Convert to base64
        audio_b64 = base64.b64encode(audio_data).decode()
        audio_url = f"data:audio/mpeg;base64,{audio_b64}"
        
        # Estimate duration (rough estimate based on text length)
        duration = len(request.text) * 0.05  # ~50ms per character
        
        # Estimate cost (ElevenLabs pricing ~$0.30 per 1000 chars)
        cost = (len(request.text) / 1000) * 0.30
        
        # Save to database
        audio = AudioGeneration(
            audio_url=audio_url,
            source="generated",
            duration=duration,
            text=request.text,
            voice_id=request.voice_id,
            voice_settings=voice_settings.model_dump(),
            cost=cost
        )

        doc = audio.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await database.insert_audio_generation(doc)

        # Track usage
        usage = TokenUsage(
            service="elevenlabs",
            operation="text_to_speech",
            cost=cost,
            details={"characters": len(request.text)}
        )
        usage_doc = usage.model_dump()
        usage_doc['timestamp'] = usage_doc['timestamp'].isoformat()
        await database.insert_token_usage(usage_doc)
        
        return {
            "success": True,
            "audio_id": audio.id,
            "audio_url": audio_url,
            "duration": duration,
            "cost": cost
        }
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/video/estimate-cost")
async def estimate_cost(request: EstimateCostRequest):
    """Estimate video generation cost"""
    try:
        cost = 0.0
        
        if request.mode == "economico":
            # Modelos gratuitos do HuggingFace
            cost = 0.0
        else:
            # Modelos premium (FAL.AI)
            if request.model == "veo3":
                if request.with_audio:
                    cost = request.duration * 0.40
                else:
                    cost = request.duration * 0.20
            elif request.model == "sora2":
                cost = request.duration * 0.10
            elif request.model == "wav2lip":
                # Wav2lip pricing (estimate)
                cost = request.duration * 0.05
        
        return {
            "success": True,
            "estimated_cost": round(cost, 2),
            "model": request.model,
            "mode": request.mode,
            "duration": request.duration,
            "with_audio": request.with_audio,
            "is_free": request.mode == "economico"
        }
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/video/test-prompt")
async def test_prompt(request: dict):
    """Test endpoint to see what prompt is received"""
    logger.info(f"🔍 TEST PROMPT RECEIVED: {request.get('prompt', 'NO PROMPT')}")
    return {"received_prompt": request.get('prompt', 'NO PROMPT')}

@api_router.get("/video/providers")
async def get_video_providers():
    """
    Lista providers de vídeo disponíveis e seus custos
    Retorna FAL.AI (sempre disponível) e Google Veo Direct (se configurado)
    """
    try:
        providers_status = video_manager.get_available_providers()
        
        providers_info = []
        
        # FAL.AI Veo 3.1
        if providers_status.get(VideoProvider.FAL_VEO3):
            providers_info.append({
                "id": "fal_veo3",
                "name": "Veo 3.1 (FAL.AI)",
                "provider": "fal",
                "description": "Google Veo 3.1 via FAL.AI - Alta qualidade, múltiplas resoluções",
                "available": True,
                "cost_per_second": 0.20,
                "cost_per_second_with_audio": 0.40,
                "max_duration": 8,
                "supports_audio": True,
                "quality": "premium"
            })
        
        # FAL.AI Sora 2
        if providers_status.get(VideoProvider.FAL_SORA2):
            providers_info.append({
                "id": "fal_sora2",
                "name": "Sora 2 (FAL.AI)",
                "provider": "fal",
                "description": "OpenAI Sora 2 via FAL.AI - Criativo e cinematográfico",
                "available": True,
                "cost_per_second": 0.15,
                "cost_per_second_with_audio": 0.30,
                "max_duration": 5,
                "supports_audio": True,
                "quality": "premium"
            })
        
        # Google Veo 3.1 Direct
        if providers_status.get(VideoProvider.GOOGLE_VEO3_DIRECT):
            providers_info.append({
                "id": "google_veo3",
                "name": "Veo 3.1 (Google Direct)",
                "provider": "google",
                "description": "Google Veo 3.1 direto via Vertex AI - 60% mais barato que FAL.AI",
                "available": True,
                "cost_per_second": 0.12,
                "cost_per_second_with_audio": 0.15,
                "max_duration": 8,
                "supports_audio": True,
                "quality": "premium",
                "savings_vs_fal": "60%"
            })
        
        return {
            "success": True,
            "providers": providers_info,
            "default_provider": "fal_veo3" if providers_status.get(VideoProvider.FAL_VEO3) else "google_veo3"
        }
    
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/video/generate")
async def generate_video(request: GenerateVideoRequest):
    """Generate video with selected model (Premium or Econômico)"""
    try:
        video_id = str(uuid.uuid4())
        
        # Function to sanitize prompt for content policy
        def sanitize_prompt(prompt):
            """Remove ALL potentially problematic content that triggers FAL.AI and Google Veo filters"""
            import re

            # STEP 1: Remove ALL mentions of facial fidelity/identity/preservation
            # These trigger DEEPFAKE DETECTION in all services
            fidelity_removal_patterns = [
                r'\[Manter[^\]]*\]',  # Remove all [Manter...] blocks
                r'\[.*?identidade.*?\]',  # Any block mentioning identity
                r'\[.*?fidelidade.*?\]',  # Any block mentioning fidelity
                r'\[.*?NÃO DEVEM.*?\]',  # Any block with NÃO DEVEM
                r'\[.*?preserv.*?\]',  # Any block mentioning preserve
                r'[Mm]anter.*?identidade[^.]*\.',  # Sentences about maintaining identity
                r'[Pp]reserv.*?fidelidade[^.]*\.',  # Sentences about preserving fidelity
                r'[Ee]xata.*?semelhança[^.]*\.',  # Exact likeness
                r'[Ii]dentidade.*?visual[^.]*\.',  # Visual identity
                r'[Cc]aracterísticas.*?físicas[^.]*?mantidas[^.]*?\.',  # Physical characteristics maintained
                r'[^.]*?expressões faciais[^.]*?fidelidade[^.]*?\.',  # Any sentence with facial expressions + fidelity
                r'[Aa]s expressões faciais devem ser preservadas[^.]*?\.',  # Specific phrase
                r'com alta fidelidade',  # Remove "with high fidelity" mentions
                r'devem ser preservadas[^.]*?fidelidade[^.]*?',  # Must be preserved with fidelity
                r'alta fidelidade[^.]*?',  # Remove "high fidelity"
                r'[^.]*?preservadas com alta fidelidade[^.]*?\.',  # Preserved with high fidelity sentence
                r'expressões faciais[^.]*?alta fidelidade[^.]*?\.',  # Facial expressions with high fidelity
                r'[Ss]emelhança.*?exata.*?',  # Exact similarity
                r'100%.*?(identidade|fidelidade|semelhança)',  # 100% identity/fidelity/likeness
            ]

            sanitized = prompt
            for pattern in fidelity_removal_patterns:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)

            # STEP 2: Replace VIOLENT and GRAPHIC content words
            violence_replacements = [
                (r'ameaçador(a|amente|es)?', 'impressionante'),
                (r'assustador(a|es)?', 'surpreendente'),
                (r'violento?(a|amente|s)?', 'intenso'),
                (r'afiado?(a|s)?', 'visível'),
                (r'ataca(r|ndo|m)?', 'aproxima'),
                (r'ataque', 'aproximação'),
                (r'medo', 'admiração'),
                (r'terror', 'impacto'),
                (r'pânico', 'intensidade'),
                (r'perigoso?(a|s)?', 'impressionante'),
                (r'sangue', 'efeito visual dramático'),
                (r'sangrento?(a|s)?', 'dramático'),
                (r'mort(e|o|a|os|as)', 'drama'),
                (r'morre(r|ndo|u|m)?', 'desaparece'),
                (r'mata(r|ndo|m|ram)?', 'neutraliza'),
                (r'agressiv(o|a|amente|os|as)', 'energétic'),
                (r'ferimento', 'marca dramática'),
                (r'ferido?(a|s)?', 'afetado'),
                (r'ferir', 'impactar'),
                (r'tortura', 'tensão extrema'),
                (r'mutilação', 'transformação'),
                (r'brutal(idade)?', 'intenso'),
            ]

            for pattern, replacement in violence_replacements:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

            # STEP 3: Replace WEAPONS mentions (contextual)
            weapons_replacements = [
                (r'\barma\b', 'objeto cênico'),
                (r'\barmas\b', 'objetos cênicos'),
                (r'\bfaca\b', 'objeto metálico'),
                (r'\bfacas\b', 'objetos metálicos'),
                (r'\bespada\b', 'lâmina cênica'),
                (r'\bpistola\b', 'objeto de cena'),
                (r'\brevólver\b', 'objeto de cena'),
            ]

            for pattern, replacement in weapons_replacements:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

            # STEP 4: Replace EXPLICIT content (if any slips through)
            explicit_replacements = [
                (r'\bnu\b', 'natural'),
                (r'\bnua\b', 'natural'),
                (r'\bnudez\b', 'naturalidade'),
                (r'\bdespido?(a|s)?\b', 'simples'),
            ]

            for pattern, replacement in explicit_replacements:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

            # STEP 5: Replace ILLEGAL ACTIVITIES
            illegal_replacements = [
                (r'\bdroga\b', 'substância'),
                (r'\bdrogas\b', 'substâncias'),
            ]

            for pattern, replacement in illegal_replacements:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

            # STEP 6: Clean up extra spaces and formatting
            sanitized = re.sub(r'\s+', ' ', sanitized)  # Multiple spaces to single
            sanitized = re.sub(r'\.\s*\.', '.', sanitized)  # Double periods
            sanitized = re.sub(r'\s+([,.])', r'\1', sanitized)  # Space before punctuation
            sanitized = sanitized.strip()

            return sanitized
        
        # Sanitize prompt
        original_prompt = request.prompt
        sanitized_prompt = sanitize_prompt(request.prompt)
        
        if original_prompt != sanitized_prompt:
            logger.warning("⚠️ PROMPT SANITIZED!")
            logger.warning(f"REMOVED {len(original_prompt) - len(sanitized_prompt)} characters")
            logger.warning(f"CLEAN PROMPT: {sanitized_prompt[:300]}")
        else:
            logger.info(f"✅ Prompt clean: {sanitized_prompt[:100]}")
        
        # Calculate cost based on mode
        cost = 0.0
        if request.mode == "premium":
            if request.model == "veo3":
                cost = request.duration * (0.40 if request.audio_url else 0.20)
            elif request.model == "sora2":
                cost = request.duration * 0.10
            elif request.model == "wav2lip":
                cost = request.duration * 0.05
        # Modo econômico é gratuito
        
        # Save initial record
        video = VideoGeneration(
            id=video_id,
            image_id=request.image_url,
            audio_id=request.audio_url,
            model=request.model,
            mode=request.mode,
            prompt=request.prompt,
            duration=request.duration,
            estimated_cost=cost,
            status="processing"
        )

        doc = video.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await database.insert_video_generation(doc)
        
        # Generate video based on model, mode, and provider
        result_url = None
        
        if request.mode == "premium":
            # Veo 3.1 - Usar provider correto (FAL.AI ou Google Direct)
            if request.model == "veo3":
                logger.info(f"🎬 Generating Veo 3.1 video with provider: {request.provider}")
                logger.info(f"   Image: {request.image_url[:100]}")
                logger.info(f"   Prompt: {sanitized_prompt}")
                logger.info(f"   Duration: {request.duration}s")
                
                # Usar video_providers.py para gerenciar providers
                from video_providers import VideoProviderManager, VideoProvider
                
                provider_manager = VideoProviderManager()
                
                # Map provider name to VideoProvider enum
                if request.provider == "google":
                    provider_enum = VideoProvider.GOOGLE_VEO3_DIRECT
                    logger.info("✅ Using Google Veo 3.1 Direct API (via veo31_direct.py)")
                else:
                    provider_enum = VideoProvider.FAL_VEO3
                    logger.info("✅ Using FAL.AI for Veo 3.1")
                
                # Generate via provider
                result = await provider_manager.generate_video(
                    provider=provider_enum,
                    image_url=request.image_url,
                    prompt=sanitized_prompt,
                    duration=request.duration
                )
                
                # VideoGenerationResult é um objeto, não dict
                result_url = result.video_url
                cost = result.cost  # Update cost with actual value
                logger.info(f"✅ Video generated successfully: {result_url}")
                logger.info(f"💰 Actual cost: ${cost:.2f}")
                
            elif request.model == "sora2":
                logger.info(f"🎬 Generating Sora 2 video with provider: {request.provider}")
                
                # Usar video_providers.py
                from video_providers import VideoProviderManager, VideoProvider
                
                provider_manager = VideoProviderManager()
                
                # Sora 2 atualmente só via FAL.AI
                provider_enum = VideoProvider.FAL_SORA2
                logger.info("✅ Using FAL.AI for Sora 2")
                
                result = await provider_manager.generate_video(
                    provider=provider_enum,
                    image_url=request.image_url,
                    prompt=sanitized_prompt,
                    duration=request.duration
                )
                
                # VideoGenerationResult é um objeto
                result_url = result.video_url
                cost = result.cost  # Update cost
                logger.info(f"✅ Sora 2 video generated: {result_url}")
                logger.info(f"💰 Actual cost: ${cost:.2f}")
                
            elif request.model == "wav2lip":
                if not request.audio_url:
                    raise HTTPException(status_code=400, detail="Audio URL required for Wav2lip")
                
                import asyncio
                handler = fal_client.submit(
                    "fal-ai/wav2lip",
                    arguments={
                        "face_url": request.image_url,
                        "audio_url": request.audio_url
                    }
                )
                # Run in executor to avoid blocking
                result = await asyncio.get_event_loop().run_in_executor(
                    None, handler.get
                )
                result_url = result.get('video', {}).get('url')
        
        elif request.mode == "economico":
            # Free models via HuggingFace Spaces
            if request.model == "open-sora":
                try:
                    # Use HuggingFace Open-Sora Space
                    hf_client = Client("hpcai-tech/Open-Sora")
                    result = hf_client.predict(
                        prompt=request.prompt,
                        image=request.image_url,
                        api_name="/predict"
                    )
                    result_url = result
                except Exception as e:
                    logger.error(f"Error with Open-Sora: {str(e)}")
                    raise HTTPException(status_code=503, detail=f"Modelo Open-Sora temporariamente indisponível. Erro: {str(e)}")
                    
            elif request.model == "wav2lip-free":
                if not request.audio_url:
                    raise HTTPException(status_code=400, detail="Audio URL required for Wav2lip")
                
                try:
                    # Use HuggingFace Wav2Lip Space (procurar space público disponível)
                    # Nota: Pode variar dependendo do space disponível
                    hf_client = Client("fffiloni/Wav2Lip")
                    result = hf_client.predict(
                        image=request.image_url,
                        audio=request.audio_url,
                        api_name="/predict"
                    )
                    result_url = result
                except Exception as e:
                    logger.error(f"Error with Wav2Lip Free: {str(e)}")
                    raise HTTPException(status_code=503, detail=f"Modelo Wav2Lip Free temporariamente indisponível. Erro: {str(e)}")
        
        # Update record
        await database.update_video_generation(video_id, {
            "status": "completed",
            "result_url": result_url,
            "cost": cost
        })

        # Track usage (only for paid services)
        if cost > 0:
            usage = TokenUsage(
                service="fal_ai",
                operation=f"video_generation_{request.model}",
                cost=cost,
                details={"duration": request.duration, "model": request.model, "mode": request.mode}
            )
            usage_doc = usage.model_dump()
            usage_doc['timestamp'] = usage_doc['timestamp'].isoformat()
            await database.insert_token_usage(usage_doc)
        
        return {
            "success": True,
            "video_id": video_id,
            "video_url": result_url,
            "cost": cost,
            "mode": request.mode,
            "is_free": request.mode == "economico"
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating video: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        logger.error(f"❌ Full error details: {repr(e)}")
        
        # Try to extract detailed error from FAL.AI response
        error_message = str(e)
        error_detail = None
        
        # Check if it's a FAL.AI API error with more details
        if hasattr(e, 'args') and len(e.args) > 0:
            error_detail = str(e.args[0])
            logger.error(f"❌ Error detail: {error_detail}")
        
        # Check for specific FAL.AI error patterns
        error_lower = error_message.lower()
        
        # Pattern 1: Actual content policy violations
        is_content_policy = (
            'content_policy_violation' in error_lower or 
            'content policy' in error_lower or
            'violates our content policy' in error_lower or
            'blocked by safety' in error_lower or
            'safety filter' in error_lower
        )
        
        # Pattern 2: Authentication/API key errors
        is_auth_error = (
            'unauthorized' in error_lower or
            'invalid api key' in error_lower or
            'authentication failed' in error_lower or
            '401' in error_message or
            '403' in error_message
        )
        
        # Pattern 3: Invalid parameters
        is_param_error = (
            'invalid parameter' in error_lower or
            'bad request' in error_lower or
            '400' in error_message or
            'validation error' in error_lower
        )
        
        # Pattern 4: Service unavailable
        is_service_error = (
            '503' in error_message or
            '502' in error_message or
            'service unavailable' in error_lower or
            'timeout' in error_lower
        )
        
        # Generate user-friendly messages based on error type
        if is_content_policy:
            friendly_message = """⚠️ Política de Conteúdo: O prompt contém termos que foram bloqueados pela política de conteúdo da IA.

Dicas para resolver:
• Evite palavras como: ameaçador, violento, ataque, sangue, armas
• Use palavras neutras: impressionante, surpreendente, dramático
• Foque na descrição visual sem conotação violenta

Exemplo: Em vez de "T-Rex ameaçador rugindo", use "T-Rex impressionante com boca aberta"."""
            error_code = "CONTENT_POLICY"
            
        elif is_auth_error:
            friendly_message = "❌ Erro de Autenticação: Chave de API FAL.AI inválida ou expirada. Verifique suas credenciais."
            error_code = "AUTH_ERROR"
            
        elif is_param_error:
            friendly_message = f"❌ Parâmetros Inválidos: {error_message}\n\nVerifique se a imagem está acessível e o prompt está correto."
            error_code = "INVALID_PARAMS"
            
        elif is_service_error:
            friendly_message = "❌ Serviço Temporariamente Indisponível: O servidor FAL.AI está sobrecarregado. Tente novamente em alguns minutos."
            error_code = "SERVICE_UNAVAILABLE"
            
        else:
            # Unknown error - show actual error message for debugging
            friendly_message = f"❌ Erro ao gerar vídeo:\n\n{error_message}\n\nDetalhes técnicos: {error_detail or 'N/A'}"
            error_code = "GENERATION_ERROR"
            logger.error(f"❌ UNKNOWN ERROR TYPE - Full message: {error_message}")
        
        # Update record with error
        await database.update_video_generation(video_id, {
            "status": "failed",
            "error": error_message
        })
        
        raise HTTPException(
            status_code=422 if error_code == "CONTENT_POLICY" else 500,
            detail={
                "error_code": error_code,
                "message": friendly_message,
                "original_error": error_message if error_code != "CONTENT_POLICY" else None
            }
        )

@api_router.post("/auth/verify")
async def verify_password(request: VerifyPasswordRequest):
    """Verify admin password"""
    admin_password = os.environ.get('ADMIN_PASSWORD', 'mauricio123')
    
    if request.password == admin_password:
        return {"success": True, "message": "Password verified"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@api_router.get("/tokens/usage")
async def get_token_usage():
    """Get token usage statistics"""
    try:
        # Get all usage records
        usage_records = await database.get_token_usage(limit=1000)

        # Calculate totals
        total_spent = sum(record.get('cost', 0) for record in usage_records)

        # Group by service
        by_service = {}
        for record in usage_records:
            service = record.get('service', 'unknown')
            if service not in by_service:
                by_service[service] = 0
            by_service[service] += record.get('cost', 0)

        # Get recent operations (last 10)
        recent = sorted(usage_records, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]

        # Get balances
        balances = await database.get_all_api_balances()

        # Calculate remaining balances
        balance_info = {}
        for balance in balances:
            service = balance.get('service')
            initial = balance.get('initial_balance', 0)
            spent = by_service.get(service, 0)
            remaining = initial - spent
            balance_info[service] = {
                "initial": round(initial, 2),
                "spent": round(spent, 2),
                "remaining": round(remaining, 2)
            }

        return {
            "success": True,
            "total_spent": round(total_spent, 2),
            "by_service": {k: round(v, 2) for k, v in by_service.items()},
            "recent_operations": recent,
            "balances": balance_info
        }
    except Exception as e:
        logger.error(f"Error getting token usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/tokens/balance")
async def update_balance(request: UpdateBalanceRequest):
    """Update or create API balance"""
    try:
        await database.upsert_api_balance(request.service, request.initial_balance)

        return {
            "success": True,
            "message": f"Saldo atualizado para {request.service}"
        }
    except Exception as e:
        logger.error(f"Error updating balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tokens/balances")
async def get_balances():
    """Get all API balances"""
    try:
        # Get all balances
        balances = await database.get_all_api_balances()

        # Get usage
        usage_records = await database.get_token_usage(limit=1000)

        # Group by service
        by_service = {}
        for record in usage_records:
            service = record.get('service', 'unknown')
            if service not in by_service:
                by_service[service] = 0
            by_service[service] += record.get('cost', 0)

        # Calculate remaining for each service
        result = {}
        for balance in balances:
            service = balance.get('service')
            initial = balance.get('initial_balance', 0)
            spent = by_service.get(service, 0)
            remaining = initial - spent
            result[service] = {
                "initial": round(initial, 2),
                "spent": round(spent, 2),
                "remaining": round(remaining, 2)
            }

        return {
            "success": True,
            "balances": result
        }
    except Exception as e:
        logger.error(f"Error getting balances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/gallery/items")
async def get_gallery_items():
    """Get all generated videos and audios for gallery"""
    try:
        # Get all videos (only completed ones)
        videos = await database.get_video_generations(status="completed", limit=100)

        # Get all audios
        audios = await database.get_audio_generations(limit=100)

        # Get all images
        images = await database.get_image_analyses(limit=100)

        return {
            "success": True,
            "videos": videos,
            "audios": audios,
            "images": images
        }
    except Exception as e:
        logger.error(f"Error getting gallery items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/gallery/video/{video_id}")
async def delete_video(video_id: str):
    """Delete a video from gallery"""
    try:
        deleted = await database.delete_video_generation(video_id)
        if deleted:
            return {"success": True, "message": "Vídeo deletado"}
        else:
            raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/gallery/audio/{audio_id}")
async def delete_audio(audio_id: str):
    """Delete an audio from gallery"""
    try:
        deleted = await database.delete_audio_generation(audio_id)
        if deleted:
            return {"success": True, "message": "Áudio deletado"}
        else:
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
    except Exception as e:
        logger.error(f"Error deleting audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/gallery/image/{image_id}")
async def delete_image(image_id: str):
    """Delete an image analysis from gallery"""
    try:
        deleted = await database.delete_image_analysis(image_id)
        if deleted:
            return {"success": True, "message": "Imagem deletada"}
        else:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== IMAGE GENERATION ENDPOINTS ====================

class ImageGenerationRequest(BaseModel):
    """Request body for image generation"""
    prompt: str
    reference_image_base64: Optional[str] = None

@api_router.post("/images/generate")
async def generate_image_with_nano_banana(request: ImageGenerationRequest):
    """Generate image using Gemini 2.0 Flash Exp with optional reference image (base64)"""

    try:
        prompt = request.prompt
        logger.info(f"🎨 Generating image with Gemini 2.0 Flash Exp: {prompt[:100]}...")

        import google.generativeai as genai
        import base64
        from PIL import Image
        from io import BytesIO

        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_KEY"))

        # Prepare content parts for generation
        content_parts = []

        # If reference image is provided (as base64), add it first
        if request.reference_image_base64:
            try:
                logger.info(f"📎 Reference image provided as base64")

                # Extract base64 data (remove data:image/...;base64, prefix if present)
                base64_data = request.reference_image_base64
                if ',' in base64_data:
                    base64_data = base64_data.split(',', 1)[1]

                # Decode and convert to PIL Image
                image_bytes = base64.b64decode(base64_data)
                pil_image = Image.open(BytesIO(image_bytes))
                logger.info(f"✅ Reference image loaded (size: {pil_image.size})")

                # Add image to content parts
                content_parts.append(pil_image)

            except Exception as img_error:
                logger.warning(f"Failed to process reference image: {str(img_error)}")

        # Add text prompt with facial preservation instruction if reference image is provided
        if request.reference_image_base64:
            # Enhance prompt to explicitly preserve facial features
            enhanced_prompt = f"""CRITICAL INSTRUCTION: You MUST keep the EXACT same person from the reference image above. Preserve their face completely - same facial features, face shape, skin tone, eyes, nose, mouth, expression, and all unique characteristics. Preserve the microtexture of the skin, including pores, fine lines, and any unique features like moles or scars. The facial structure, proportions, and all traits must be replicated with photographic precision. The lighting and shadows on the face must remain consistent with the reference image to maintain the exact volume and shape. Only change the setting, clothing, pose, and styling as described below. DO NOT change the person's face or identity.

{prompt}

REMINDER: The face in the output image MUST be identical to the face in the reference image."""
            content_parts.append(enhanced_prompt)
            logger.info(f"✅ Enhanced prompt with facial preservation instructions")
        else:
            content_parts.append(prompt)

        # Configure generation settings for high quality
        generation_config = {
            "temperature": 0.2,  # Low temperature for maximum consistency and facial preservation
            "top_p": 0.95,       # High top_p for quality while maintaining determinism
            "top_k": 30,         # Reduced for more deterministic results
        }

        # Add resolution instructions to prompt
        if request.reference_image_base64:
            # Append resolution requirement to existing enhanced prompt
            content_parts[-1] = content_parts[-1] + "\n\nOUTPUT SPECIFICATIONS: Generate in the HIGHEST RESOLUTION possible. Target 2K or 4K quality (minimum 2048x2048 pixels). Professional photography quality with sharp details, high definition, and maximum clarity suitable for large format printing."
        else:
            # Add to regular prompt
            content_parts[-1] = content_parts[-1] + "\n\nOUTPUT SPECIFICATIONS: Generate in the HIGHEST RESOLUTION possible. Target 2K or 4K quality (minimum 2048x2048 pixels). Professional photography quality with sharp details, high definition, and maximum clarity suitable for large format printing."

        # Create model instance
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-image",  # Official model for image generation
            generation_config=generation_config
        )

        logger.info(f"🎨 Calling Gemini 2.5 Flash Image with HIGH RESOLUTION request...")

        # Generate image
        response = model.generate_content(content_parts)

        logger.info(f"✅ Gemini generation completed")

        # Extract image from response
        image_data = None
        text_response = None

        for part in response.candidates[0].content.parts:
            # Check for text (for debugging)
            if hasattr(part, 'text') and part.text:
                text_response = part.text
                logger.warning(f"⚠️ Gemini returned text instead of image: {text_response[:200]}...")

            # Check for inline data (images)
            if hasattr(part, 'inline_data') and part.inline_data:
                # Convert to base64
                image_bytes = part.inline_data.data
                image_data = base64.b64encode(image_bytes).decode('utf-8')
                mime_type = part.inline_data.mime_type
                image_url = f"data:{mime_type};base64,{image_data}"
                
                # Calculate image dimensions for logging
                try:
                    pil_img = Image.open(BytesIO(image_bytes))
                    width, height = pil_img.size
                    megapixels = (width * height) / 1_000_000
                    logger.info(f"✅ HIGH RESOLUTION Image extracted: {width}x{height} ({megapixels:.2f}MP), size: {len(image_data)} chars, type: {mime_type}")
                except:
                    logger.info(f"✅ Image extracted (size: {len(image_data)} chars, type: {mime_type})")
                break

        if not image_data:
            error_msg = "No image generated by Gemini."
            if text_response:
                error_msg += f" Gemini returned text instead: '{text_response[:100]}...'"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        image_id = str(uuid.uuid4())

        # Save to database
        generated_image = GeneratedImage(
            id=image_id,
            prompt=prompt,
            image_url=image_url,
            cost=0.00  # Gemini 2.0 Flash Exp is free during preview
        )

        doc = generated_image.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await database.insert_generated_image(doc)

        # Track cost (Gemini 2.5 Flash Image is free during preview period)
        usage = TokenUsage(
            service="Gemini 2.5 Flash Image Generation",
            operation="generate_image",
            cost=0.00,
            details={
                "prompt_length": len(prompt),
                "model": "gemini-2.5-flash-image",
                "has_reference_image": request.reference_image_base64 is not None
            }
        )
        usage_doc = usage.model_dump()
        usage_doc['timestamp'] = usage_doc['timestamp'].isoformat()
        await database.insert_token_usage(usage_doc)

        return {
            "success": True,
            "image_id": image_id,
            "image_url": image_url,
            "prompt": prompt,
            "cost": 0.039
        }

    except Exception as e:
        logger.error(f"Error generating image with Gemini: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/images/generated")
async def get_generated_images():
    """Get all generated images"""
    try:
        images = await database.get_generated_images(limit=100)

        return {
            "success": True,
            "images": images
        }
    except Exception as e:
        logger.error(f"Error fetching generated images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/images/generated/{image_id}")
async def delete_generated_image(image_id: str):
    """Delete a generated image"""
    try:
        deleted = await database.delete_generated_image(image_id)

        if deleted:
            return {"success": True, "message": "Generated image deleted"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        logger.error(f"Error deleting generated image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROOT ENDPOINTS ====================

@app.get("/")
async def root():
    """API Root - Returns basic information"""
    return {
        "name": "Talking Photo Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api": "/api",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        await database.init_db()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "api": "ok",
                "database": "ok",
                "cloudinary": "configured" if os.environ.get('CLOUDINARY_CLOUD_NAME') else "not_configured",
                "gemini": "configured" if os.environ.get('GEMINI_KEY') else "not_configured",
                "elevenlabs": "configured" if os.environ.get('ELEVENLABS_KEY') else "not_configured",
                "fal": "configured" if os.environ.get('FAL_KEY') else "not_configured"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db():
    """Initialize SQLite database on startup"""
    await database.init_db()
    logger.info("✅ SQLite database initialized successfully")