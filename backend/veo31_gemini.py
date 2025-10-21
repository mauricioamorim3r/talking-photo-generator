"""
Google Veo 3.1 via Gemini API - Video Generation
Official implementation using google-genai SDK

Authentication: API Key (GEMINI_KEY)
Model: veo-3.1-generate-preview
Cost: ~$0.005 per second (62% cheaper than FAL.AI)

Documentation:
https://ai.google.dev/gemini-api/docs/video?hl=pt-br
https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb
"""

import os
import time
import base64
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
import io

from google import genai
from google.genai import types

class Veo31GeminiGenerator:
    """Google Veo 3.1 video generator via Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Veo 3.1 generator
        
        Args:
            api_key: Gemini API key (from GEMINI_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv("GEMINI_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_KEY not found in environment variables")
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        # Default model
        self.model = "veo-3.1-generate-preview"
        
        print(f"✅ Veo 3.1 Gemini initialized with API Key: {self.api_key[:20]}...")
    
    def _image_to_genai_format(self, image_path: str) -> types.Image:
        """
        Convert image file to Gemini API format
        
        Args:
            image_path: Path to the image file
            
        Returns:
            types.Image object for Gemini API
        """
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Detect MIME type
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
            mime_type = 'image/jpeg'
        elif image_path.lower().endswith('.webp'):
            mime_type = 'image/webp'
        else:
            mime_type = 'image/jpeg'  # Default
        
        # Create Image object
        return types.Image(
            image_bytes=image_data,
            mime_type=mime_type
        )
    
    def generate_video_from_image(
        self,
        prompt: str,
        image_path: str,
        duration_seconds: int = 8,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate video from image using Veo 3.1
        
        Args:
            prompt: Text description of the video animation
            image_path: Path to the input image
            duration_seconds: Video duration (4, 6, or 8 seconds)
            resolution: Video resolution ("720p" or "1080p")
            aspect_ratio: Video aspect ratio ("16:9" or "9:16")
            output_path: Optional path to save the video
            
        Returns:
            Path to the generated video file
        """
        print(f"\n{'='*60}")
        print(f"🎬 Veo 3.1 Gemini - Image to Video Generation")
        print(f"{'='*60}")
        print(f"📝 Prompt: {prompt}")
        print(f"🖼️  Image: {image_path}")
        print(f"⏱️  Duration: {duration_seconds}s")
        print(f"📺 Resolution: {resolution}")
        print(f"📐 Aspect Ratio: {aspect_ratio}")
        
        # Convert image to Gemini format
        image = self._image_to_genai_format(image_path)
        
        # Start video generation (async operation)
        print(f"\n🚀 Starting video generation...")
        operation = self.client.models.generate_videos(
            model=self.model,
            prompt=prompt,
            image=image,
            config=types.GenerateVideosConfig(
                duration_seconds=duration_seconds,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                number_of_videos=1
            )
        )
        
        print(f"⏳ Operation started: {operation.name}")
        
        # Poll until video is ready (can take 11 seconds to 6 minutes)
        poll_count = 0
        while not operation.done:
            poll_count += 1
            elapsed = poll_count * 10
            print(f"⏳ Waiting for video generation... ({elapsed}s elapsed)")
            time.sleep(10)
            operation = self.client.operations.get(operation)
        
        print(f"\n✅ Video generation complete! (Total time: {poll_count * 10}s)")
        
        # Get generated video
        generated_video = operation.response.generated_videos[0]
        
        # Determine output path
        if not output_path:
            timestamp = int(time.time())
            output_path = f"veo31_video_{timestamp}.mp4"
        
        # Download video
        print(f"💾 Downloading video to: {output_path}")
        self.client.files.download(file=generated_video.video)
        generated_video.video.save(output_path)
        
        print(f"✅ Video saved successfully!")
        print(f"{'='*60}\n")
        
        return output_path
    
    def generate_video_text_only(
        self,
        prompt: str,
        duration_seconds: int = 8,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate video from text prompt only (text-to-video)
        
        Args:
            prompt: Text description of the video
            duration_seconds: Video duration (4, 6, or 8 seconds)
            resolution: Video resolution ("720p" or "1080p")
            aspect_ratio: Video aspect ratio ("16:9" or "9:16")
            negative_prompt: Optional text describing what NOT to include
            output_path: Optional path to save the video
            
        Returns:
            Path to the generated video file
        """
        print(f"\n{'='*60}")
        print(f"🎬 Veo 3.1 Gemini - Text to Video Generation")
        print(f"{'='*60}")
        print(f"📝 Prompt: {prompt}")
        if negative_prompt:
            print(f"🚫 Negative: {negative_prompt}")
        print(f"⏱️  Duration: {duration_seconds}s")
        print(f"📺 Resolution: {resolution}")
        print(f"📐 Aspect Ratio: {aspect_ratio}")
        
        # Start video generation
        print(f"\n🚀 Starting video generation...")
        
        config = types.GenerateVideosConfig(
            duration_seconds=duration_seconds,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            number_of_videos=1
        )
        
        if negative_prompt:
            config.negative_prompt = negative_prompt
        
        operation = self.client.models.generate_videos(
            model=self.model,
            prompt=prompt,
            config=config
        )
        
        print(f"⏳ Operation started: {operation.name}")
        
        # Poll until video is ready
        poll_count = 0
        while not operation.done:
            poll_count += 1
            elapsed = poll_count * 10
            print(f"⏳ Waiting for video generation... ({elapsed}s elapsed)")
            time.sleep(10)
            operation = self.client.operations.get(operation)
        
        print(f"\n✅ Video generation complete! (Total time: {poll_count * 10}s)")
        
        # Get generated video
        generated_video = operation.response.generated_videos[0]
        
        # Determine output path
        if not output_path:
            timestamp = int(time.time())
            output_path = f"veo31_video_{timestamp}.mp4"
        
        # Download video
        print(f"💾 Downloading video to: {output_path}")
        self.client.files.download(file=generated_video.video)
        generated_video.video.save(output_path)
        
        print(f"✅ Video saved successfully!")
        print(f"{'='*60}\n")
        
        return output_path


# Async wrapper for server integration
async def generate_video_veo31_gemini(
    prompt: str,
    image_path: str,
    duration_seconds: int = 8,
    resolution: str = "720p",
    aspect_ratio: str = "16:9"
) -> str:
    """
    Async wrapper for Veo 3.1 Gemini video generation
    
    Args:
        prompt: Text description of the video animation
        image_path: Path to the input image
        duration_seconds: Video duration (4, 6, or 8 seconds)
        resolution: Video resolution ("720p" or "1080p")
        aspect_ratio: Video aspect ratio ("16:9" or "9:16")
        
    Returns:
        Path to the generated video file
    """
    generator = Veo31GeminiGenerator()
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        generator.generate_video_from_image,
        prompt,
        image_path,
        duration_seconds,
        resolution,
        aspect_ratio,
        None  # output_path
    )


# Simple sync function for testing
def generate_video_veo31_gemini_sync(
    prompt: str,
    image_path: str,
    duration_seconds: int = 8
) -> str:
    """
    Synchronous helper for Veo 3.1 Gemini generation
    
    Args:
        prompt: Text description of the video animation
        image_path: Path to the input image
        duration_seconds: Video duration (4, 6, or 8 seconds)
        
    Returns:
        Path to the generated video file
    """
    generator = Veo31GeminiGenerator()
    return generator.generate_video_from_image(
        prompt=prompt,
        image_path=image_path,
        duration_seconds=duration_seconds
    )
