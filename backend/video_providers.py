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
    GOOGLE_VEO3_DIRECT = "google_veo3"


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
        self.google_available = self._check_google()
        
        logger.info(f"🎬 Video Providers Disponíveis:")
        logger.info(f"  - FAL.AI: {'✅' if self.fal_available else '❌'}")
        logger.info(f"  - Google Veo Direct: {'✅' if self.google_available else '❌'}")
    
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
    
    def _check_google(self) -> bool:
        """Verifica se Google Vertex AI está configurado (API Key simplificado)"""
        # Método simplificado: apenas verifica se API Key existe
        api_key = os.getenv("GOOGLE_VERTEX_API_KEY")
        
        if not api_key:
            logger.warning("⚠️ Google Vertex AI não configurado (GOOGLE_VERTEX_API_KEY faltando)")
            return False
        
        logger.info("✅ Google Vertex AI configurado (API Key)")
        return True
    
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
        
        elif provider == VideoProvider.GOOGLE_VEO3_DIRECT:
            return await self._generate_via_google(image_url, prompt, duration, with_audio, aspect_ratio)
        
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
            VideoProvider.FAL_SORA2: "fal-ai/sora-turbo/image-to-video",
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
    
    async def _generate_via_google(
        self,
        image_url: str,
        prompt: str,
        duration: int,
        with_audio: bool,
        aspect_ratio: str
    ) -> VideoGenerationResult:
        """Gera vídeo via Google Veo 3.1 Direct"""
        
        if not self.google_available:
            raise RuntimeError(
                "Google Veo Direct não está disponível. "
                "Configure GOOGLE_VERTEX_API_KEY no .env"
            )
        
        logger.info(f"🎬 Gerando vídeo via Google Veo 3.1 Direct: {prompt[:50]}...")
        
        # Import dinâmico da versão simplificada
        from veo31_simple import Veo31DirectSimple
        
        # Cria cliente (usa API Key do .env)
        veo_client = Veo31DirectSimple()
        
        # Gera vídeo (async)
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            veo_client.generate_video_from_image,
            image_url,
            prompt,
            duration,
            with_audio,
            aspect_ratio
        )
        
        logger.info(f"✅ Vídeo gerado via Google! Custo: ${result['cost']:.2f}")
        
        return VideoGenerationResult(
            video_url=result['video_url'],
            provider="google_veo3",
            duration=result['duration'],
            cost=result['cost'],
            with_audio=with_audio,
            status=result['status']
        )
    
    def estimate_cost(
        self,
        provider: VideoProvider,
        duration: int,
        with_audio: bool = False
    ) -> float:
        """Estima custo de geração"""
        
        cost_table = {
            VideoProvider.FAL_VEO3: 0.40 if with_audio else 0.20,
            VideoProvider.FAL_SORA2: 0.30 if with_audio else 0.15,
            VideoProvider.FAL_WAV2LIP: 0.10,
            VideoProvider.GOOGLE_VEO3_DIRECT: 0.15 if with_audio else 0.12
        }
        
        cost_per_sec = cost_table.get(provider, 0.20)
        return duration * cost_per_sec


# Instância global
video_manager = VideoProviderManager()
