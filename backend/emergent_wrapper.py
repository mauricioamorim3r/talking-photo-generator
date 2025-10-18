"""
Wrapper to replace emergentintegrations with google-generativeai
"""
import google.generativeai as genai
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import base64


class FileContentWithMimeType:
    """File content wrapper"""
    def __init__(self, file_path: str, mime_type: str):
        self.file_path = file_path
        self.mime_type = mime_type


class UserMessage:
    """User message wrapper"""
    def __init__(self, text: str, file_contents: Optional[List[FileContentWithMimeType]] = None):
        self.text = text
        self.file_contents = file_contents or []


class LlmChat:
    """Chat wrapper for Google Gemini"""

    def __init__(self, api_key: str, session_id: str, system_message: str = ""):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self.model_name = "gemini-2.0-flash-exp"  # Default model
        self.model_params = {}

        # Configure the API
        genai.configure(api_key=api_key)

    def with_model(self, provider: str, model: str):
        """Set the model to use"""
        self.model_name = model
        return self

    def with_params(self, **kwargs):
        """Set additional parameters"""
        self.model_params = kwargs
        return self

    async def send_message(self, message: UserMessage) -> str:
        """Send message and get text response"""
        try:
            # Create model
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }

            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                system_instruction=self.system_message if self.system_message else None
            )

            # Prepare content
            content_parts = []

            # Add file contents if present
            for file_content in message.file_contents:
                with open(file_content.file_path, 'rb') as f:
                    image_data = f.read()
                    content_parts.append({
                        'mime_type': file_content.mime_type,
                        'data': image_data
                    })

            # Add text
            content_parts.append(message.text)

            # Generate response
            response = model.generate_content(content_parts)

            return response.text

        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}")

    async def send_message_multimodal_response(self, message: UserMessage) -> tuple[str, List[Dict[str, Any]]]:
        """Send message and get multimodal response (text + images)"""
        try:
            # For image generation, use the appropriate model
            if 'image' in self.model_params.get('modalities', []):
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                )

                # Generate image
                response = model.generate_content(message.text)

                images = []
                text_response = ""

                # Check if response contains images
                if hasattr(response, 'candidates') and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            # Check for text
                            if hasattr(part, 'text') and part.text:
                                text_response = part.text

                            # Check for inline data (images)
                            if hasattr(part, 'inline_data'):
                                image_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                                images.append({
                                    'data': image_data,
                                    'mime_type': part.inline_data.mime_type
                                })

                return text_response, images
            else:
                # Regular text response
                text = await self.send_message(message)
                return text, []

        except Exception as e:
            raise Exception(f"Error generating multimodal content: {str(e)}")
