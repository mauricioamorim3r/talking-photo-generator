"""
Video Generation Providers - Unified Interface
Suporta múltiplos providers: FAL.AI, Google Veo Direct, etc.
"""

import os
import asyncio
import logging
from typing import Literal, Optional, Dict, Any
from enum import Enum
from pathlib import Path

# Load .env if exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

logger = logging.getLogger(__name__)


class VideoProvider(str, Enum):
    """Providers disponíveis para geração de vídeo"""
    FAL_VEO3 = "fal_veo3"
    FAL_SORA2 = "fal_sora2"
    FAL_WAV2LIP = "fal_wav2lip"
    GOOGLE_VEO31_GEMINI = "google_veo31_gemini"  # Novo: Gemini API (62% mais barato)
    GOOGLE_VEO3_DIRECT = "google_veo3"  # Deprecado: Vertex AI (modelo ainda não disponível)


class VideoGenerationResult:
    """Resultado unificado de geração de vídeo"""
    def __init__(
        self,
        video_url: str,
        provider: str,
        duration: int,
        cost: float,
        with_audio: bool = False,
        status: str = "success"
    ):
        self.video_url = video_url
        self.provider = provider
        self.duration = duration
        self.cost = cost
        self.with_audio = with_audio
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_url": self.video_url,
            "provider": self.provider,
            "duration": self.duration,
            "cost": self.cost,
            "with_audio": self.with_audio,
            "status": self.status
        }


class VideoProviderManager:
    """Gerencia múltiplos providers de geração de vídeo"""
    
    def __init__(self):
        self.fal_available = self._check_fal()
        self.google_gemini_available = self._check_google_gemini()
        self.google_vertex_available = self._check_google_vertex()
        
        logger.info(f"🎬 Video Providers Disponíveis:")
        logger.info(f"  - FAL.AI: {'✅' if self.fal_available else '❌'}")
        logger.info(f"  - Google Veo 3.1 (Gemini API): {'✅' if self.google_gemini_available else '❌'}")
        logger.info(f"  - Google Veo Direct (Vertex): {'✅' if self.google_vertex_available else '❌'}")
    
    def _check_fal(self) -> bool:
        """Verifica se FAL.AI está configurado"""
        try:
            import fal_client
            fal_key = os.getenv("FAL_KEY")
            if not fal_key:
                logger.warning("⚠️ FAL_KEY não configurada")
                return False
            return True
        except ImportError:
            logger.warning("⚠️ fal_client não instalado")
            return False
    
    def _check_google_gemini(self) -> bool:
        """Verifica se Google Gemini API está configurado (Veo 3.1)"""
        gemini_key = os.getenv("GEMINI_KEY")
        
        if gemini_key:
            logger.info("✅ Google Veo 3.1 (Gemini API) configurado")
            return True
        
        logger.warning("⚠️ GEMINI_KEY não configurada")
        return False
    
    def _check_google_vertex(self) -> bool:
        """Verifica se Google Vertex AI está configurado (Deprecado - modelo não disponível)"""
        # Método 1: API Key (mais simples e rápido)
        api_key = os.getenv("GOOGLE_VERTEX_API_KEY")
        
        if api_key:
            logger.info("✅ Google Veo Direct configurado (API Key)")
            return True
        
        # Método 2: Service Account (mais completo, mas requer mais setup)
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if project_id and credentials and os.path.exists(credentials):
            logger.info("✅ Google Veo Direct configurado (Service Account)")
            return True
        
        logger.warning("⚠️ Google Veo Direct não configurado")
        logger.warning("   Configure GOOGLE_VERTEX_API_KEY ou (GOOGLE_CLOUD_PROJECT_ID + GOOGLE_APPLICATION_CREDENTIALS)")
        return False
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Retorna lista de providers disponíveis"""
        return {
            VideoProvider.FAL_VEO3: self.fal_available,
            VideoProvider.FAL_SORA2: self.fal_available,
            VideoProvider.FAL_WAV2LIP: self.fal_available,
            VideoProvider.GOOGLE_VEO3_DIRECT: self.google_available
        }
    
    async def generate_video(
        self,
        provider: VideoProvider,
        image_url: str,
        prompt: str,
        duration: int = 8,
        with_audio: bool = False,
        aspect_ratio: str = "16:9"
    ) -> VideoGenerationResult:
        """
        Gera vídeo usando o provider especificado
        
        Args:
            provider: Provider a ser usado (fal_veo3, google_veo3, etc)
            image_url: URL da imagem base
            prompt: Prompt de geração
            duration: Duração em segundos
            with_audio: Se deve gerar áudio
            aspect_ratio: Proporção (16:9, 9:16, etc)
        
        Returns:
            VideoGenerationResult com video_url e custos
        """
        
        if provider in [VideoProvider.FAL_VEO3, VideoProvider.FAL_SORA2, VideoProvider.FAL_WAV2LIP]:
            return await self._generate_via_fal(provider, image_url, prompt, duration, with_audio)
        
        elif provider == VideoProvider.GOOGLE_VEO31_GEMINI:
            return await self._generate_via_google_gemini(image_url, prompt, duration, with_audio, aspect_ratio)
        
        elif provider == VideoProvider.GOOGLE_VEO3_DIRECT:
            return await self._generate_via_google_vertex(image_url, prompt, duration, with_audio, aspect_ratio)
        
        else:
            raise ValueError(f"Provider não suportado: {provider}")
    
    async def _generate_via_fal(
        self,
        provider: VideoProvider,
        image_url: str,
        prompt: str,
        duration: int,
        with_audio: bool
    ) -> VideoGenerationResult:
        """Gera vídeo via FAL.AI"""
        
        if not self.fal_available:
            raise RuntimeError("FAL.AI não está disponível. Verifique FAL_KEY.")
        
        import fal_client
        
        # Mapeia provider para endpoint FAL
        endpoint_map = {
            VideoProvider.FAL_VEO3: "fal-ai/veo3.1/image-to-video",
            VideoProvider.FAL_SORA2: "fal-ai/sora-2/image-to-video",
            VideoProvider.FAL_WAV2LIP: "fal-ai/wav2lip"
        }
        
        endpoint = endpoint_map.get(provider)
        
        # Argumentos base
        args = {
            "image_url": image_url,
            "prompt": prompt
        }
        
        # Adiciona duração se suportado
        if provider == VideoProvider.FAL_VEO3:
            args["duration"] = f"{duration}s"
        
        logger.info(f"🎬 Gerando vídeo via FAL.AI ({provider}): {prompt[:50]}...")
        
        # Submete job
        handler = fal_client.submit(endpoint, arguments=args)
        
        # Aguarda resultado (async)
        result = await asyncio.get_event_loop().run_in_executor(
            None, handler.get
        )
        
        video_url = result.get('video', {}).get('url')
        
        if not video_url:
            raise RuntimeError(f"FAL.AI não retornou video_url: {result}")
        
        # Calcula custo
        if provider == VideoProvider.FAL_VEO3:
            cost_per_sec = 0.40 if with_audio else 0.20
        elif provider == VideoProvider.FAL_SORA2:
            cost_per_sec = 0.30 if with_audio else 0.15
        else:
            cost_per_sec = 0.10
        
        cost = duration * cost_per_sec
        
        logger.info(f"✅ Vídeo gerado via FAL.AI! Custo: ${cost:.2f}")
        
        return VideoGenerationResult(
            video_url=video_url,
            provider=str(provider),
            duration=duration,
            cost=cost,
            with_audio=with_audio,
            status="success"
        )
    
    async def _generate_via_google_gemini(
        self,
        image_url: str,
        prompt: str,
        duration: int,
        with_audio: bool,
        aspect_ratio: str
    ) -> VideoGenerationResult:
        """Gera vídeo via Google Veo 3.1 (Gemini API) - 62% mais barato"""
        
        if not self.google_gemini_available:
            raise RuntimeError(
                "Google Veo 3.1 (Gemini API) não está disponível. "
                "Configure GEMINI_KEY no arquivo .env"
            )
        
        logger.info(f"🎬 Gerando vídeo via Google Veo 3.1 (Gemini API): {prompt[:50]}...")
        
        from veo31_gemini import generate_video_veo31_gemini
        
        # Download image locally (Gemini API requires local file)
        import tempfile
        import requests
        
        # Download image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(response.content)
            temp_image_path = tmp_file.name
        
        try:
            # Generate video
            video_path = await generate_video_veo31_gemini(
                prompt=prompt,
                image_path=temp_image_path,
                duration_seconds=duration,
                resolution="720p",
                aspect_ratio=aspect_ratio
            )
            
            # Upload video to get URL (você pode usar Cloudinary ou outro serviço)
            # Por enquanto, retorna path local
            video_url = f"file://{video_path}"
            
            # Calcula custo (Gemini API é 62% mais barato que FAL.AI)
            # FAL.AI: $0.20/sec sem áudio, $0.40/sec com áudio
            # Gemini: $0.076/sec (fixo, com áudio nativo)
            cost = duration * 0.076
            
            logger.info(f"✅ Vídeo gerado via Gemini! Custo: ${cost:.2f} (62% economia)")
            
            return VideoGenerationResult(
                video_url=video_url,
                provider="google_veo31_gemini",
                duration=duration,
                cost=cost,
                with_audio=True,  # Veo 3.1 sempre gera com áudio
                status="success"
            )
        
        finally:
            # Clean up temp file
            import os
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
    
    async def _generate_via_google_vertex(
        self,
        image_url: str,
        prompt: str,
        duration: int,
        with_audio: bool,
        aspect_ratio: str
    ) -> VideoGenerationResult:
        """Gera vídeo via Google Veo Direct (Vertex AI) - DEPRECADO: modelo não disponível"""
        
        if not self.google_vertex_available:
            raise RuntimeError(
                "Google Veo Direct (Vertex) não está disponível. "
                "NOTA: Este modelo ainda não está liberado publicamente. "
                "Use google_veo31_gemini ao invés."
            )
        
        logger.warning("⚠️ Google Veo Direct (Vertex) ainda não está disponível publicamente")
        logger.info("💡 Sugestão: Use provider 'google_veo31_gemini' (Gemini API)")
        
        raise RuntimeError(
            "Google Veo 3.1 Direct (Vertex AI) ainda não está disponível publicamente. "
            "Use provider 'google_veo31_gemini' para acessar via Gemini API."
        )
    
    def estimate_cost(
        self,
        provider: VideoProvider,
        duration: int,
        with_audio: bool = False
    ) -> float:
        """
        Estima custo de geração
        
        Tabela de preços (USD por segundo):
        - FAL Veo 3: $0.40/s (com áudio) ou $0.20/s (sem áudio)
        - FAL Sora 2: $0.30/s (com áudio) ou $0.15/s (sem áudio)
        - FAL Wav2Lip: $0.10/s
        - Google Veo 3.1 (Gemini): $0.076/s (com áudio nativo) - 62% ECONOMIA! 🎉
        - Google Veo Direct (Vertex): Não disponível ainda
        """
        
        cost_table = {
            VideoProvider.FAL_VEO3: 0.40 if with_audio else 0.20,
            VideoProvider.FAL_SORA2: 0.30 if with_audio else 0.15,
            VideoProvider.FAL_WAV2LIP: 0.10,
            VideoProvider.GOOGLE_VEO31_GEMINI: 0.076,  # Sempre com áudio, 62% mais barato!
            VideoProvider.GOOGLE_VEO3_DIRECT: 999.99  # Não disponível (erro se usado)
        }
        
        cost_per_sec = cost_table.get(provider, 0.20)
        return duration * cost_per_sec


# Instância global
video_manager = VideoProviderManager()
