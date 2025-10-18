from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
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
    model: Literal["veo3", "sora2", "wav2lip"]
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
    model: Literal["veo3", "sora2", "wav2lip"]
    prompt: str
    audio_url: Optional[str] = None
    duration: Optional[int] = 5

class EstimateCostRequest(BaseModel):
    model: Literal["veo3", "sora2", "wav2lip"]
    duration: int
    with_audio: bool = False

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
            folder="video-gen",
            upload_preset=os.environ.get('CLOUDINARY_UPLOAD_PRESET', 'ml_default')
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
    """Analyze image with Gemini and suggest best model"""
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
            system_message="""Você é um especialista em análise de imagens para geração de vídeos animados. 
            Analise a imagem e sugira o melhor modelo:
            - Veo 3: Melhor para cenas complexas, movimentos naturais, alta qualidade geral
            - Sora 2: Melhor para animações rápidas, custo-benefício, boa qualidade
            - Wav2lip: Melhor quando já existe vídeo e precisa sincronizar lábios com áudio
            
            Responda em formato JSON:
            {
              "description": "Descrição detalhada da imagem",
              "subject_type": "pessoa/animal/objeto/boneco",
              "recommended_model": "veo3/sora2/wav2lip",
              "reason": "Motivo da recomendação",
              "tips": "Dicas para o prompt"
            }"""
        ).with_model("gemini", "gemini-2.0-flash")
        
        image_file = FileContentWithMimeType(
            file_path=temp_path,
            mime_type="image/jpeg"
        )
        
        user_message = UserMessage(
            text="Analise esta imagem e sugira o melhor modelo para animá-la.",
            file_contents=[image_file]
        )
        
        response = await chat.send_message(user_message)
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Parse response
        import json
        analysis_data = json.loads(response.strip('```json').strip('```').strip())
        
        # Save to database
        analysis = ImageAnalysis(
            image_url=request.image_url,
            analysis=json.dumps(analysis_data),
            suggested_model=analysis_data.get('recommended_model', 'veo3')
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
            "duration": request.duration,
            "with_audio": request.with_audio
        }
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/video/generate")
async def generate_video(request: GenerateVideoRequest):
    """Generate video with selected model"""
    try:
        video_id = str(uuid.uuid4())
        
        # Calculate cost
        cost = 0.0
        if request.model == "veo3":
            cost = request.duration * (0.40 if request.audio_url else 0.20)
        elif request.model == "sora2":
            cost = request.duration * 0.10
        elif request.model == "wav2lip":
            cost = request.duration * 0.05
        
        # Save initial record
        video = VideoGeneration(
            id=video_id,
            image_id=request.image_url,
            audio_id=request.audio_url,
            model=request.model,
            prompt=request.prompt,
            duration=request.duration,
            estimated_cost=cost,
            status="processing"
        )
        
        doc = video.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.video_generations.insert_one(doc)
        
        # Generate video based on model
        result_url = None
        
        if request.model == "veo3":
            handler = await fal_client.submit(
                "fal-ai/veo3.1/image-to-video",
                arguments={
                    "image_url": request.image_url,
                    "prompt": request.prompt,
                    "duration": request.duration
                }
            )
            result = await handler.get()
            result_url = result.get('video', {}).get('url')
            
        elif request.model == "sora2":
            handler = await fal_client.submit(
                "fal-ai/sora-2/image-to-video",
                arguments={
                    "image_url": request.image_url,
                    "prompt": request.prompt
                }
            )
            result = await handler.get()
            result_url = result.get('video', {}).get('url')
            
        elif request.model == "wav2lip":
            if not request.audio_url:
                raise HTTPException(status_code=400, detail="Audio URL required for Wav2lip")
            
            handler = await fal_client.submit(
                "fal-ai/wav2lip",
                arguments={
                    "face_url": request.image_url,
                    "audio_url": request.audio_url
                }
            )
            result = await handler.get()
            result_url = result.get('video', {}).get('url')
        
        # Update record
        await db.video_generations.update_one(
            {"id": video_id},
            {"$set": {
                "status": "completed",
                "result_url": result_url,
                "cost": cost
            }}
        )
        
        # Track usage
        usage = TokenUsage(
            service="fal_ai",
            operation=f"video_generation_{request.model}",
            cost=cost,
            details={"duration": request.duration, "model": request.model}
        )
        usage_doc = usage.model_dump()
        usage_doc['timestamp'] = usage_doc['timestamp'].isoformat()
        await db.token_usage.insert_one(usage_doc)
        
        return {
            "success": True,
            "video_id": video_id,
            "video_url": result_url,
            "cost": cost
        }
        
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        
        # Update record with error
        await db.video_generations.update_one(
            {"id": video_id},
            {"$set": {
                "status": "failed",
                "error": str(e)
            }}
        )
        
        raise HTTPException(status_code=500, detail=str(e))

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