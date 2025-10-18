from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone
import fal_client
from elevenlabs import ElevenLabs
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
import cloudinary
import cloudinary.uploader
import base64
import io
from PIL import Image
from gradio_client import Client

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'video_gen_database')]

# Configure APIs
fal_key = os.environ.get('FAL_KEY', '')
os.environ['FAL_KEY'] = fal_key

elevenlabs_client = ElevenLabs(api_key=os.environ.get('ELEVENLABS_KEY', ''))

# Backend URL for serving images
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET', '')
)

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
    model: Literal["veo3", "sora2", "wav2lip", "open-sora", "wav2lip-free"]
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
    image_url: str

class GenerateAudioRequest(BaseModel):
    text: str
    voice_id: str = "cgSgspJ2msm6clMCkdW9"  # Default child voice
    stability: float = 0.5
    similarity_boost: float = 0.75
    speed: float = 1.0
    style: float = 0.0

class GenerateVideoRequest(BaseModel):
    image_url: str
    model: Literal["veo3", "sora2", "wav2lip", "open-sora", "wav2lip-free"]
    mode: Literal["premium", "economico"] = "premium"
    prompt: str
    audio_url: Optional[str] = None
    duration: Optional[int] = 5
    cinematic_settings: Optional[dict] = None

class EstimateCostRequest(BaseModel):
    model: Literal["veo3", "sora2", "wav2lip", "open-sora", "wav2lip-free"]
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

@api_router.post("/images/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload image to Cloudinary"""
    try:
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="video-gen"
        )
        
        return {
            "success": True,
            "image_url": result['secure_url'],
            "cloudinary_id": result['public_id']
        }
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/images/analyze")
async def analyze_image(request: AnalyzeImageRequest):
    """Analyze image with Gemini and suggest best model with cinematic prompts"""
    try:
        # Download image
        import requests
        img_response = requests.get(request.image_url)
        img_data = img_response.content
        
        # Save temporarily
        temp_path = f"/tmp/{uuid.uuid4()}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(img_data)
        
        # Analyze with Gemini
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY', ''),
            session_id=str(uuid.uuid4()),
            system_message="""Você é um diretor de fotografia especialista em criar prompts cinematográficos otimizados para Sora 2 e Veo 3.

**🚨 POLÍTICA DE CONTEÚDO CRÍTICA 🚨**
NUNCA mencione ou inclua QUALQUER referência a:
- "manter identidade facial", "preservar características faciais", "fidelidade facial", "não alterar rosto"
- "100% da identidade", "expressões faciais devem ser preservadas", "características originais"
- "alta fidelidade", "exatamente como na foto", "sem modificar o rosto"

❌ ESTES TERMOS VIOLAM A POLÍTICA ANTI-DEEPFAKE E BLOQUEIAM A GERAÇÃO ❌

Os modelos JÁ mantêm a imagem original automaticamente. Descreva apenas a AÇÃO e MOVIMENTO desejados.

**PALAVRAS PROIBIDAS:**
❌ ameaçador, violento, ataque, sangue, armas, terror, pânico, agressivo, afiado
✅ USE ESTAS: impressionante, dramático, majestoso, intenso, impactante, surpreendente, admirável

---

## 📽️ TEMPLATE ESPECÍFICO PARA SORA 2

**Quando usar**: Cenas com física realista, movimento de personagens, ambientes detalhados

**Estrutura do Prompt para Sora 2 (7 Camadas):**
```
1. [CENA E AMBIENTE]: ambiente, hora do dia, clima, atmosfera
2. [SUJEITO E AÇÃO]: quem/o que está na cena, movimento principal, emoções, ritmo
3. [PHYSICS & MATERIALS]: texturas, interações físicas, comportamento de materiais (tecido, pelo, água, poeira)
4. [CINEMATOGRAFIA]: tipo de plano, movimento de câmera, lente, framing
5. [ILUMINAÇÃO E COR]: fontes de luz, direção, mood, paleta de cores
6. [ÁUDIO]: sons de fala, efeitos sonoros, ambiente, música (Sora 2 gera áudio nativo)
7. [QUALIDADE + EXCLUSÕES]: resolução, estilo, texturas + sem watermarks/artifacts
```

**Exemplo Sora 2 Refinado:**
"Campo de flores silvestres ao amanhecer, névoa leve sobre o solo, atmosfera serena e mágica. Golden retriever correndo com energia natural, orelhas balançando ao vento, língua para fora, expressão alegre, patas tocando o solo com movimento rítmico. Física realista: pelo texturizado movendo-se com o vento, flores balançando suavemente, gotas de orvalho visíveis nas pétalas. Medium shot transitando para wide shot, câmera acompanha o movimento com dolly suave lateral. Lente 50mm com shallow depth of field, foco no cachorro. Iluminação golden hour: luz quente e suave lateral, raios de sol filtrados através das flores criando lens flare natural, sombras longas. Paleta: tons âmbar e verdes vibrantes. Áudio sincronizado: sons rítmicos de patas na grama, respiração energética do cachorro, vento suave rustling nas flores, pássaros cantando ao fundo. Filmado em 35mm, cinematic color grading, 4K, texturas ultra-detalhadas de pelo e vegetação. Sem watermarks, sem text overlays, sem artifacts digitais."

---

## 📽️ TEMPLATE ESPECÍFICO PARA VEO 3

**Quando usar**: Produção cinematográfica de alta qualidade, áudio sincronizado complexo, motion realism extremo

**Estrutura do Prompt para Veo 3 (Profissional):**
```
1. [AÇÃO PRINCIPAL]: movimento detalhado e específico do sujeito, timing, transições
2. [CINEMATIC SHOT]: tipo de plano profissional + movimento de câmera técnico
3. [LENTE E FOCO]: especificações exatas (focal length, aperture, depth of field)
4. [LIGHTING DESIGN]: setup de iluminação profissional (key, fill, rim, bounce)
5. [COLOR GRADING]: paleta cinematográfica específica, mood, look references
6. [AUDIO DESIGN]: camadas de som ambiente, foley, música, sincronização precisa
7. [QUALIDADE & EXCLUSÕES]: hyper-realistic, resolução 4K/8K, estilo de filmagem + sem distrações
```

**Exemplo Veo 3 Refinado:**
"Mulher de cabelos longos virando a cabeça lentamente em 3 segundos para a câmera, sorriso surgindo gradualmente frame by frame, olhos brilhando com luz refletida, cabelo fluindo naturalmente com movimento suave e orgânico, micro-expressões faciais detalhadas. Close-up cinematográfico, câmera estática em tripod profissional com rack focus suave transicionando do fundo desfocado para o rosto nítido. Shot com lente prime 85mm f/1.4, bokeh cremoso hexagonal no background, shallow depth of field isolando o sujeito. Three-point lighting setup: key light LED suave de 45° criando sombras naturais, fill light difuso reduzindo contraste, rim light backlight destacando o contorno do cabelo com halo sutil. Color grading cinematográfico: tons quentes (amber/gold) nas highlights, teal frio nos shadows, contraste médio, saturação controlada, look de filme comercial premium. Audio design em camadas: ambiente suave de café com conversas distantes a 20%, som sutil de movimento de roupa, respiração natural baixa, música instrumental melancólica de piano ao fundo, tudo sincronizado com o movimento. Hyper-realistic 4K, textura de pele ultra-detalhada com poros visíveis, cabelo com strand definition, filmado em estilo de luxury commercial high-end production. Sem watermarks, sem lower thirds, sem lens flares excessivos, color grading consistente."

---

## 🎬 TEMPLATES SIMPLIFICADOS (Modelos Econômicos)

**Para Open-Sora (gratuito):**
"[Sujeito] fazendo [ação]. [Tipo de plano]. [Iluminação básica]. [Movimento natural]. Qualidade cinematográfica."

**Para Wav2lip (sincronização labial):**
"[Pessoa] falando diretamente para a câmera. Close-up. Boa iluminação. Movimento labial sincronizado. HD quality."

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
            """Clean all prompts in analysis data"""
            problematic_words = {
                'ameaçador': 'impressionante',
                'ameaçadora': 'impressionante',
                'ameaçadoramente': 'impressionantemente',
                'assustador': 'surpreendente',
                'assustadora': 'surpreendente',
                'violento': 'intenso',
                'violenta': 'intensa',
                'afiados': 'visíveis',
                'afiado': 'visível',
                'afiada': 'visível',
                'ataque': 'aproximação',
                'atacar': 'se aproximar',
                'atacando': 'se aproximando',
                'medo': 'admiração',
                'terror': 'impacto',
                'pânico': 'reação intensa',
                'sangue': 'efeito dramático',
                'morte': 'drama',
                'agressiv': 'energétic'
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
        
        # Save to database
        analysis = ImageAnalysis(
            image_url=request.image_url,
            analysis=json.dumps(analysis_data),
            suggested_model=analysis_data.get('recommended_model_premium', 'veo3')
        )
        
        doc = analysis.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.image_analyses.insert_one(doc)
        
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
        await db.audio_generations.insert_one(doc)
        
        # Track usage
        usage = TokenUsage(
            service="elevenlabs",
            operation="text_to_speech",
            cost=cost,
            details={"characters": len(request.text)}
        )
        usage_doc = usage.model_dump()
        usage_doc['timestamp'] = usage_doc['timestamp'].isoformat()
        await db.token_usage.insert_one(usage_doc)
        
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

@api_router.post("/video/generate")
async def generate_video(request: GenerateVideoRequest):
    """Generate video with selected model (Premium or Econômico)"""
    try:
        video_id = str(uuid.uuid4())
        
        # Function to sanitize prompt for content policy
        def sanitize_prompt(prompt):
            """Remove ALL potentially problematic content that triggers FAL.AI filters"""
            import re
            
            # STEP 1: Remove ALL mentions of facial fidelity/identity/preservation
            # These trigger deepfake detection
            fidelity_removal_patterns = [
                r'\[Manter[^\]]*\]',  # Remove all [Manter...] blocks
                r'\[.*?identidade.*?\]',  # Any block mentioning identity
                r'\[.*?fidelidade.*?\]',  # Any block mentioning fidelity
                r'\[.*?NÃO DEVEM.*?\]',  # Any block with NÃO DEVEM
                r'\[.*?preserv.*?\]',  # Any block mentioning preserve
                r'[Mm]anter.*?identidade[^.]*\.',  # Sentences about maintaining identity
                r'[Pp]reserv.*?fidelidade[^.]*\.',  # Sentences about preserving fidelity
                r'[^.]*?expressões faciais[^.]*?fidelidade[^.]*?\.',  # Any sentence with facial expressions + fidelity
                r'[Aa]s expressões faciais devem ser preservadas[^.]*?\.',  # Specific phrase
                r'com alta fidelidade',  # Remove "with high fidelity" mentions
                r'devem ser preservadas[^.]*?fidelidade[^.]*?',  # Must be preserved with fidelity
                r'alta fidelidade[^.]*?',  # Remove "high fidelity"
                r'[^.]*?preservadas com alta fidelidade[^.]*?\.',  # Preserved with high fidelity sentence
                r'expressões faciais[^.]*?alta fidelidade[^.]*?\.',  # Facial expressions with high fidelity
            ]
            
            sanitized = prompt
            for pattern in fidelity_removal_patterns:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            
            # STEP 2: Remove violent/threatening words
            word_replacements = [
                (r'ameaçador(a|amente|es)?', 'impressionante'),
                (r'assustador(a|es)?', 'surpreendente'),
                (r'violento?(a|s)?', 'intenso'),
                (r'afiado?(a|s)?', 'visível'),
                (r'ataca(r|ndo|m)?', 'aproxima'),
                (r'ataque', 'aproximação'),
                (r'medo', 'admiração'),
                (r'terror', 'impacto'),
                (r'pânico', 'intensidade'),
                (r'perigoso?(a|s)?', 'impressionante')
            ]
            
            for pattern, replacement in word_replacements:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
            # STEP 3: Clean up extra spaces and formatting
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
        await db.video_generations.insert_one(doc)
        
        # Generate video based on model and mode
        result_url = None
        
        if request.mode == "premium":
            # Premium models via FAL.AI
            if request.model == "veo3":
                import asyncio
                handler = fal_client.submit(
                    "fal-ai/veo3.1/image-to-video",
                    arguments={
                        "image_url": request.image_url,
                        "prompt": sanitized_prompt,  # Use sanitized prompt
                        "duration": request.duration
                    }
                )
                # Run in executor to avoid blocking
                result = await asyncio.get_event_loop().run_in_executor(
                    None, handler.get
                )
                result_url = result.get('video', {}).get('url')
                
            elif request.model == "sora2":
                import asyncio
                handler = fal_client.submit(
                    "fal-ai/sora-2/image-to-video",
                    arguments={
                        "image_url": request.image_url,
                        "prompt": sanitized_prompt  # Use sanitized prompt
                    }
                )
                # Run in executor to avoid blocking
                result = await asyncio.get_event_loop().run_in_executor(
                    None, handler.get
                )
                result_url = result.get('video', {}).get('url')
                
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
        await db.video_generations.update_one(
            {"id": video_id},
            {"$set": {
                "status": "completed",
                "result_url": result_url,
                "cost": cost
            }}
        )
        
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
            await db.token_usage.insert_one(usage_doc)
        
        return {
            "success": True,
            "video_id": video_id,
            "video_url": result_url,
            "cost": cost,
            "mode": request.mode,
            "is_free": request.mode == "economico"
        }
        
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        
        # Check if it's a content policy violation
        error_message = str(e)
        if 'content_policy_violation' in error_message or 'content checker' in error_message:
            friendly_message = """⚠️ Política de Conteúdo: O prompt contém termos que foram bloqueados pela política de conteúdo da IA.

Dicas para resolver:
• Evite palavras como: ameaçador, violento, ataque, sangue, armas
• Use palavras neutras: impressionante, surpreendente, dramático
• Foque na descrição visual sem conotação violenta

Exemplo: Em vez de "T-Rex ameaçador rugindo", use "T-Rex impressionante com boca aberta"."""
            error_code = "CONTENT_POLICY"
        else:
            friendly_message = f"Erro ao gerar vídeo: {error_message}"
            error_code = "GENERATION_ERROR"
        
        # Update record with error
        await db.video_generations.update_one(
            {"id": video_id},
            {"$set": {
                "status": "failed",
                "error": error_message
            }}
        )
        
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
        usage_records = await db.token_usage.find({}, {"_id": 0}).to_list(1000)
        
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
        balances = await db.api_balances.find({}, {"_id": 0}).to_list(100)
        
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
        # Check if balance exists
        existing = await db.api_balances.find_one({"service": request.service})
        
        if existing:
            # Update existing
            await db.api_balances.update_one(
                {"service": request.service},
                {"$set": {
                    "initial_balance": request.initial_balance,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }}
            )
        else:
            # Create new
            balance = APIBalance(
                service=request.service,
                initial_balance=request.initial_balance,
                current_balance=request.initial_balance
            )
            doc = balance.model_dump()
            doc['last_updated'] = doc['last_updated'].isoformat()
            await db.api_balances.insert_one(doc)
        
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
        balances = await db.api_balances.find({}, {"_id": 0}).to_list(100)
        
        # Get usage
        usage_records = await db.token_usage.find({}, {"_id": 0}).to_list(1000)
        
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
        # Get all videos
        videos = await db.video_generations.find(
            {"status": "completed"},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(100)
        
        # Get all audios
        audios = await db.audio_generations.find(
            {},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(100)
        
        # Get all images
        images = await db.image_analyses.find(
            {},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(100)
        
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
        result = await db.video_generations.delete_one({"id": video_id})
        if result.deleted_count > 0:
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
        result = await db.audio_generations.delete_one({"id": audio_id})
        if result.deleted_count > 0:
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
        result = await db.image_analyses.delete_one({"id": image_id})
        if result.deleted_count > 0:
            return {"success": True, "message": "Imagem deletada"}
        else:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()