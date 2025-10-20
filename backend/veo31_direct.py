"""
Implementação do Veo 3.1 via Google Vertex AI (SEM FAL.AI)
Economia de ~60-75% nos custos de geração de vídeo!

Setup para localhost:
1. Criar projeto: https://console.cloud.google.com
2. Ativar API: Vertex AI API
3. Service Account com role "Vertex AI User"
4. Download JSON key para ./backend/veo-service-account.json
5. Configurar .env:
   GOOGLE_CLOUD_PROJECT_ID=seu-projeto-id
   GOOGLE_APPLICATION_CREDENTIALS=./veo-service-account.json
"""

import os
import base64
import requests
from typing import Optional, Dict, Any
import logging
import time

# Google Cloud SDK é opcional - só precisa se quiser usar Veo Direct
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google Cloud SDK não instalado. Para usar Veo Direct, instale:")
    print("   pip install google-cloud-aiplatform")

logger = logging.getLogger(__name__)


class Veo31DirectAPI:
    """
    Wrapper para usar Veo 3.1 diretamente do Google Vertex AI
    sem intermediários (FAL.AI)
    """
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        Args:
            project_id: GCP Project ID
            location: Region (us-central1, europe-west4, etc)
        """
        self.project_id = project_id
        self.location = location
        self.endpoint = f"https://{location}-aiplatform.googleapis.com/v1"
        
        # Authenticate with service account or ADC
        self.credentials = self._get_credentials()
        
    def _get_credentials(self):
        """Get credentials from environment or service account file"""
        # Option 1: Service Account JSON
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            credentials = service_account.Credentials.from_service_account_file(
                os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        # Option 2: Use existing credentials
        else:
            from google.auth import default
            credentials, _ = default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        
        return credentials
    
    def _get_access_token(self):
        """Get fresh access token"""
        self.credentials.refresh(Request())
        return self.credentials.token
    
    def generate_video_from_image(
        self,
        image_url: str,
        prompt: str,
        duration_seconds: int = 8,
        with_audio: bool = False,
        aspect_ratio: str = "16:9"
    ) -> dict:
        """
        Generate video from image using Veo 3.1
        
        Args:
            image_url: URL da imagem ou base64
            prompt: Prompt cinematográfico
            duration_seconds: Duração (2-8 segundos)
            with_audio: Se deve gerar áudio
            aspect_ratio: 16:9, 9:16, 1:1
            
        Returns:
            {
                "video_url": "gs://bucket/video.mp4",
                "status": "completed",
                "duration": 8,
                "cost": 1.20
            }
        """
        
        # Prepare request
        url = f"{self.endpoint}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.1:generateVideo"
        
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [{
                "image": {
                    "bytesBase64Encoded": self._image_to_base64(image_url)
                },
                "prompt": prompt,
                "parameters": {
                    "duration": f"{duration_seconds}s",
                    "aspectRatio": aspect_ratio,
                    "generateAudio": with_audio
                }
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Parse response
        video_data = result.get("predictions", [{}])[0]
        
        return {
            "video_url": video_data.get("videoUri"),
            "status": "completed",
            "duration": duration_seconds,
            "cost": self._calculate_cost(duration_seconds, with_audio),
            "metadata": video_data.get("metadata", {})
        }
    
    def _image_to_base64(self, image_url: str) -> str:
        """Convert image URL to base64"""
        if image_url.startswith("data:image"):
            # Already base64
            return image_url.split(",")[1]
        else:
            # Download and encode
            response = requests.get(image_url)
            return base64.b64encode(response.content).decode()
    
    def _calculate_cost(self, duration: int, with_audio: bool) -> float:
        """
        Calculate estimated cost based on Google pricing
        (valores aproximados - verificar pricing oficial)
        """
        base_cost = 0.12  # ~$0.12 per second
        audio_cost = 0.03 if with_audio else 0  # ~$0.03 extra for audio
        
        return duration * (base_cost + audio_cost)


# ==========================================
# IMPLEMENTAÇÃO NO SERVER.PY
# ==========================================

async def generate_video_veo31_direct(
    image_url: str,
    prompt: str,
    duration: int = 8,
    with_audio: bool = False
) -> dict:
    """
    Generate video using Veo 3.1 DIRECT from Google
    (replacement for FAL.AI veo3.1)
    """
    import asyncio
    
    # Initialize Veo client
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    veo_client = Veo31DirectAPI(project_id=project_id)
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        veo_client.generate_video_from_image,
        image_url,
        prompt,
        duration,
        with_audio
    )
    
    return result


# ==========================================
# EXEMPLO DE USO NO ENDPOINT
# ==========================================

@api_router.post("/video/generate")
async def generate_video(request: GenerateVideoRequest):
    """Generate video - agora com opção de usar Veo direto"""
    
    if request.mode == "premium" and request.model == "veo3":
        
        # OPÇÃO 1: Via FAL.AI (atual - mais caro)
        if os.getenv("USE_FALAI_VEO") == "true":
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
            cost = 8 * 0.40  # $3.20 for 8s with audio
        
        # OPÇÃO 2: Via Google Direto (NOVO - mais barato)
        else:
            result = await generate_video_veo31_direct(
                image_url=request.image_url,
                prompt=request.prompt,
                duration=8,
                with_audio=True
            )
            result_url = result['video_url']
            cost = result['cost']  # ~$0.96-1.20 for 8s
        
        return {
            "success": True,
            "video_url": result_url,
            "cost": cost,
            "provider": "google-direct" if not os.getenv("USE_FALAI_VEO") else "fal-ai"
        }
