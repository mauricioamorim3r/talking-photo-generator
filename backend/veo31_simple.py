"""
Veo 3.1 Direct - Simplified API Key Version
Usa Google Vertex AI com API Key (mais simples que service account)
"""

import os
import base64
import requests
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class Veo31DirectSimple:
    """
    Wrapper simplificado para Veo 3.1 usando API Key
    Mais fácil de configurar que service account
    """
    
    def __init__(self, api_key: Optional[str] = None, location: str = "us-central1"):
        """
        Args:
            api_key: Google Vertex AI API Key (ou via env GOOGLE_VERTEX_API_KEY)
            location: Region (us-central1, europe-west4)
        """
        self.api_key = api_key or os.getenv("GOOGLE_VERTEX_API_KEY")
        self.location = location
        
        if not self.api_key:
            raise ValueError(
                "Google Vertex API Key não encontrada. "
                "Configure GOOGLE_VERTEX_API_KEY no .env"
            )
        
        logger.info(f"✅ Veo 3.1 Direct configurado (region: {location})")
    
    def _image_to_base64(self, image_url: str) -> str:
        """Convert image URL or path to base64"""
        try:
            if image_url.startswith(('http://', 'https://')):
                # Download from URL
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                image_bytes = response.content
            else:
                # Read from file
                with open(image_url, 'rb') as f:
                    image_bytes = f.read()
            
            return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting image: {e}")
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
        Generate video from image using Veo 3.1
        
        Args:
            image_url: URL da imagem ou caminho local
            prompt: Prompt cinematográfico
            duration_seconds: Duração (2-8 segundos)
            with_audio: Se deve gerar áudio
            aspect_ratio: 16:9, 9:16, 1:1
            
        Returns:
            {
                "video_url": "https://storage.googleapis.com/...",
                "status": "completed",
                "duration": 8,
                "cost": 1.20,
                "provider": "google_veo3"
            }
        """
        
        logger.info(f"🎬 Generating video with Veo 3.1 Direct...")
        logger.info(f"   Duration: {duration_seconds}s")
        logger.info(f"   Audio: {with_audio}")
        logger.info(f"   Prompt: {prompt[:80]}...")
        
        try:
            # 1. Convert image to base64
            image_b64 = self._image_to_base64(image_url)
            
            # 2. Prepare request
            # Nota: Esta é a API do Vertex AI Veo
            # Endpoint pode variar - ajustar conforme documentação oficial
            endpoint = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/{self.location}/publishers/google/models/veo-3.1:generateVideo"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "instances": [{
                    "image": {
                        "bytesBase64Encoded": image_b64
                    },
                    "prompt": prompt,
                    "parameters": {
                        "duration": f"{duration_seconds}s",
                        "aspectRatio": aspect_ratio,
                        "generateAudio": with_audio
                    }
                }]
            }
            
            # 3. Submit request
            logger.info(f"📡 Sending request to Vertex AI...")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=300)
            
            if response.status_code != 200:
                error_msg = f"Vertex AI error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            result = response.json()
            
            # 4. Extract video URL
            # Estrutura de resposta pode variar - ajustar conforme API real
            video_url = result.get('predictions', [{}])[0].get('videoUri') or result.get('video_url')
            
            if not video_url:
                raise RuntimeError(f"No video URL in response: {result}")
            
            # 5. Calculate cost
            # Google Veo 3.1 pricing (estimado)
            # Base: $0.12/seg sem áudio, $0.15/seg com áudio
            cost_per_sec = 0.15 if with_audio else 0.12
            total_cost = duration_seconds * cost_per_sec
            
            logger.info(f"✅ Video generated successfully!")
            logger.info(f"   URL: {video_url[:80]}...")
            logger.info(f"   Cost: ${total_cost:.2f}")
            
            return {
                "video_url": video_url,
                "status": "completed",
                "duration": duration_seconds,
                "cost": round(total_cost, 2),
                "provider": "google_veo3",
                "with_audio": with_audio
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating video: {e}")
            raise


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
