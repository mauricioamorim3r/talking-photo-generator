"""
Veo 3.1 Direct - REST API Version
Usa Google Vertex AI REST API com suporte para API Key
"""

import os
import base64
import logging
import time
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class Veo31DirectSimple:
    """
    Wrapper simplificado para Veo 3.1 usando REST API
    Suporta tanto API Key quanto Service Account
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None, location: str = "us-central1"):
        """
        Args:
            api_key: Google API Key (ou via env GOOGLE_VERTEX_API_KEY)
            project_id: GCP Project ID (ou via env GOOGLE_CLOUD_PROJECT)
            location: Region (us-central1, europe-west4)
        """
        self.api_key = api_key or os.getenv("GOOGLE_VERTEX_API_KEY")
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "talking-photo-gen-441622")
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1"
        self.access_token = None
        
        # Detecta método de autenticação
        if self.api_key:
            logger.info("✅ Using API Key authentication")
        else:
            # Tenta usar Service Account
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                logger.info(f"✅ Using Service Account authentication: {credentials_path}")
                self._load_service_account_token()
            else:
                logger.warning(
                    "⚠️ Nenhuma autenticação configurada. "
                    "Configure GOOGLE_VERTEX_API_KEY ou GOOGLE_APPLICATION_CREDENTIALS no .env"
                )
        
        logger.info(f"✅ Veo 3.1 Direct configurado (project: {self.project_id}, region: {location})")
    
    def _load_service_account_token(self):
        """Load access token from Service Account credentials"""
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            # Carrega credenciais
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Obtém token
            credentials.refresh(Request())
            self.access_token = credentials.token
            
            logger.info("✅ Service Account token obtained successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading Service Account credentials: {e}")
            raise
    
    def _load_image_bytes(self, image_url: str) -> bytes:
        """Load image from URL or local file"""
        try:
            if image_url.startswith(('http://', 'https://')):
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                return response.content
            else:
                with open(image_url, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise
    
    def generate_video_from_image(
        self,
        image_url: str,
        prompt: str,
        duration_seconds: int = 8,
        with_audio: bool = False,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Generate video from image using Veo 3.1 via REST API
        
        Args:
            image_url: URL da imagem ou caminho local
            prompt: Prompt cinematográfico
            duration_seconds: Duração (2-8 segundos)
            with_audio: Se deve gerar áudio
            aspect_ratio: 16:9, 9:16, 1:1
            
        Returns:
            {
                "video_url": "https://...",
                "status": "completed",
                "duration": 8,
                "cost": 1.20,
                "provider": "google_veo3"
            }
        """
        
        logger.info(f"🎬 Generating video with Veo 3.1 Direct (REST API)...")
        logger.info(f"   Duration: {duration_seconds}s")
        logger.info(f"   Audio: {with_audio}")
        logger.info(f"   Prompt: {prompt[:80]}...")
        
        try:
            # Carrega imagem e converte para base64
            image_bytes = self._load_image_bytes(image_url)
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Endpoint da API
            endpoint = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.1:predict"
            
            # Headers
            headers = {
                "Content-Type": "application/json",
            }
            
            # Autenticação: API Key ou Service Account
            if self.api_key:
                endpoint += f"?key={self.api_key}"
            elif self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            else:
                raise RuntimeError("No authentication configured (API Key or Service Account)")
            
            # Request payload
            payload = {
                "instances": [{
                    "prompt": prompt,
                    "image": {
                        "bytesBase64Encoded": image_b64
                    }
                }],
                "parameters": {
                    "aspectRatio": aspect_ratio,
                    "durationSeconds": duration_seconds,
                    "generateAudio": with_audio,
                    "personGeneration": "allow_adult",
                    "enhancePrompt": True
                }
            }
            
            # Faz request
            logger.info(f"📡 Sending request to Vertex AI...")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            
            result = response.json()
            
            # Extrai URL do vídeo
            if "predictions" in result and len(result["predictions"]) > 0:
                prediction = result["predictions"][0]
                video_url = prediction.get("videoUri") or prediction.get("video")
                
                logger.info(f"✅ Video generated successfully!")
                
                return {
                    "video_url": video_url,
                    "status": "completed",
                    "duration": duration_seconds,
                    "resolution": "1080p",
                    "cost": 1.20,
                    "provider": "google_veo3",
                    "with_audio": with_audio
                }
            else:
                raise ValueError(f"Unexpected response format: {result}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Error generating video: {e}")
            raise


# Helper function for direct use
def generate_video_veo31(
    prompt: str,
    duration: int = 5,
    resolution: str = "720p",
    api_key: Optional[str] = None,
    project_id: Optional[str] = None,
    location: str = "us-central1",
    image_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Direct function to generate video with Veo 3.1
    
    Args:
        prompt: Text description of the video
        duration: Duration in seconds (2-8)
        resolution: 720p or 1080p
        api_key: Google API Key (optional, reads from env)
        project_id: GCP Project ID (optional, reads from env)
        location: GCP region
        image_url: Optional image to generate from
        
    Returns:
        Dict with video_url, status, duration, cost, provider
    """
    client = Veo31DirectSimple(api_key=api_key, project_id=project_id, location=location)
    
    if image_url:
        return client.generate_video_from_image(
            image_url=image_url,
            prompt=prompt,
            duration_seconds=duration,
            aspect_ratio="16:9"
        )
    else:
        # Text-to-video not implemented yet
        raise NotImplementedError("Text-to-video not available yet. Use image_url parameter.")


# Function para usar no server.py
async def generate_video_veo31_direct(
    image_url: str,
    prompt: str,
    duration: int = 8,
    with_audio: bool = False,
    aspect_ratio: str = "16:9"
) -> Dict[str, Any]:
    """
    Async wrapper for Veo 3.1 Direct
    Compatible with server.py
    """
    import asyncio
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_VERTEX_API_KEY")
    
    if not api_key:
        raise RuntimeError(
            "GOOGLE_VERTEX_API_KEY não configurada. "
            "Adicione ao backend/.env para usar Veo Direct"
        )
    
    # Create client
    veo_client = Veo31DirectSimple(api_key=api_key)
    
    # Run in executor (não bloqueia)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        veo_client.generate_video_from_image,
        image_url,
        prompt,
        duration,
        with_audio,
        aspect_ratio
    )
    
    return result


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test
    try:
        client = Veo31DirectSimple()
        print("✅ Veo 3.1 Direct client initialized successfully!")
        print(f"   API Key: {client.api_key[:20]}...")
        
        # Test with dummy data (não vai funcionar sem imagem real)
        # result = client.generate_video_from_image(
        #     image_url="https://example.com/image.jpg",
        #     prompt="A child playing in a park",
        #     duration_seconds=8,
        #     with_audio=True
        # )
        # print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
