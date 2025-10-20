"""
Veo 3.1 Direct - Simplified API Version
Usa Google Vertex AI SDK (mais simples e direto)
"""

import os
import base64
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class Veo31DirectSimple:
    """
    Wrapper simplificado para Veo 3.1 usando Vertex AI SDK
    Requer: pip install google-cloud-aiplatform
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None, location: str = "us-central1"):
        """
        Args:
            api_key: Google API Key (ou via env GOOGLE_VERTEX_API_KEY)
            project_id: GCP Project ID (ou via env GOOGLE_CLOUD_PROJECT_ID)
            location: Region (us-central1, europe-west4)
        """
        self.api_key = api_key or os.getenv("GOOGLE_VERTEX_API_KEY")
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT_ID") or "seu-projeto-id"
        self.location = location
        
        if not self.api_key:
            logger.warning(
                "⚠️ Google Vertex API Key não encontrada. "
                "Configure GOOGLE_VERTEX_API_KEY no .env"
            )
        
        # Tenta importar SDK do Vertex AI
        try:
            import vertexai
            from vertexai import types
            
            # Inicializa Vertex AI com API Key
            os.environ["GOOGLE_API_KEY"] = self.api_key
            vertexai.init(project=self.project_id, location=self.location)
            
            self.vertexai = vertexai
            self.types = types
            logger.info(f"✅ Veo 3.1 Direct configurado (project: {self.project_id}, region: {location})")
            
        except ImportError:
            logger.error("❌ google-cloud-aiplatform não instalado!")
            logger.error("   Instale com: pip install google-cloud-aiplatform")
            raise RuntimeError("google-cloud-aiplatform necessário para Veo Direct")
    
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
        Generate video from image using Veo 3.1 via Vertex AI SDK
        
        Args:
            image_url: URL da imagem ou caminho local
            prompt: Prompt cinematográfico
            duration_seconds: Duração (2-8 segundos)
            with_audio: Se deve gerar áudio
            aspect_ratio: 16:9, 9:16, 1:1
            
        Returns:
            {
                "video_url": "gs://bucket/video.mp4" ou bytes,
                "status": "completed",
                "duration": 8,
                "cost": 1.20,
                "provider": "google_veo3"
            }
        """
        
        logger.info(f"🎬 Generating video with Veo 3.1 Direct via SDK...")
        logger.info(f"   Duration: {duration_seconds}s")
        logger.info(f"   Audio: {with_audio}")
        logger.info(f"   Prompt: {prompt[:80]}...")
        
        try:
            # Importa o cliente do Vertex AI
            from vertexai.preview.vision_models import VideoGenerationModel
            
            # Carrega o modelo
            video_model = VideoGenerationModel.from_pretrained("veo-3.1")
            
            # Carrega a imagem
            image_bytes = self._load_image_bytes(image_url)
            image = self.types.Image(image_bytes=image_bytes)
            
            # Configura parâmetros
            config = self.types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                number_of_videos=1,
                duration_seconds=duration_seconds,
                resolution="1080p",
                person_generation="allow_adult",
                enhance_prompt=True,
                generate_audio=with_audio,
            )
            
            # Gera vídeo
            logger.info(f"📡 Sending request to Vertex AI...")
            operation = video_model.generate_videos(
                prompt=prompt,
                image=image,
                config=config
            )
            
            # Aguarda conclusão (polling)
            logger.info(f"⏳ Waiting for video generation...")
            while not operation.done:
                time.sleep(10)
                logger.info(f"   Status: {operation.metadata if hasattr(operation, 'metadata') else 'processing'}...")
            
            # Extrai resultado
            if operation.response:
                generated_video = operation.result.generated_videos[0]
                
                # Pode retornar bytes ou URI
                video_data = generated_video.video.video_bytes if hasattr(generated_video.video, 'video_bytes') else None
                video_uri = generated_video.video.uri if hasattr(generated_video.video, 'uri') else None
                
                # Calcula custo
                cost_per_sec = 0.15 if with_audio else 0.12
                total_cost = duration_seconds * cost_per_sec
                
                logger.info(f"✅ Video generated successfully!")
                logger.info(f"   Cost: ${total_cost:.2f}")
                
                return {
                    "video_url": video_uri or self._save_video_bytes(video_data),
                    "video_bytes": video_data,
                    "status": "completed",
                    "duration": duration_seconds,
                    "cost": round(total_cost, 2),
                    "provider": "google_veo3",
                    "with_audio": with_audio
                }
            else:
                raise RuntimeError(f"No response from Vertex AI: {operation}")
                
        except Exception as e:
            logger.error(f"❌ Error generating video: {e}")
            raise
    
    def _load_image_bytes(self, image_url: str) -> bytes:
        """Load image from URL or file path"""
        import requests
        
        if image_url.startswith(('http://', 'https://')):
            # Download from URL
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return response.content
        else:
            # Read from file
            with open(image_url, 'rb') as f:
                return f.read()
    
    def _save_video_bytes(self, video_bytes: bytes) -> str:
        """Save video bytes to temp file and return path"""
        if not video_bytes:
            return ""
        
        import tempfile
        
        # Salva em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(video_bytes)
        temp_file.close()
        
        logger.info(f"💾 Video saved to: {temp_file.name}")
        return temp_file.name


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
