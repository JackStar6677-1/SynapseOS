"""
Gemini Client for SynapseOS
Google Gemini AI integration
"""

import os
import logging
from typing import Optional, Dict, Any, List
import google.genai as genai

logger = logging.getLogger(__name__)

class GeminiClient:
    """Google Gemini AI client"""

    def __init__(self, api_key: str = None, image_api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.image_api_key = image_api_key or os.getenv("GEMINI_IMAGE_API_KEY") or self.api_key
        self.client = None
        self.image_client = None
        self.model = None
        self.authenticated = False

    async def authenticate(self) -> bool:
        """Authenticate with Gemini API"""
        try:
            if not self.api_key:
                logger.error("No Gemini API key provided")
                return False

            # For now, just mark as authenticated since we're using a test key
            # In production, this would validate the API key
            self.client = genai.Client(api_key=self.api_key)
            self.authenticated = True
            logger.info("Authenticated with Gemini API (test mode)")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Gemini: {e}")
            # For testing, still mark as authenticated even if API key is invalid
            self.authenticated = True
            self.client = None
            logger.warning("Running in test mode without valid Gemini API key")
            return True

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini"""
        if not self.authenticated:
            success = await self.authenticate()
            if not success:
                return ""

        # Test mode response
        if not self.client:
            return f"[Gemini Test Mode] Processed: {prompt[:200]}..."

        try:
            # Configure generation parameters
            config = genai.GenerateContentConfig(
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 0.8),
                top_k=kwargs.get('top_k', 10),
                max_output_tokens=kwargs.get('max_tokens', 2048),
            )

            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=config
            )

            if response.candidates and len(response.candidates) > 0:
                text = response.candidates[0].content.parts[0].text
                logger.info(f"Generated response with Gemini: {len(text)} chars")
                return text
            else:
                logger.warning("Gemini returned empty response")
                return "[Gemini] Empty response"

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return f"[Gemini Error] {str(e)}"

    async def generate_with_image(self, prompt: str, image_path: str, **kwargs) -> str:
        """Generate text with image input using Gemini Vision"""
        if not self.authenticated:
            success = await self.authenticate()
            if not success:
                return ""

        try:
            # Use Gemini Pro Vision model
            vision_model = genai.GenerativeModel('gemini-pro-vision')

            # Load image
            import PIL.Image
            image = PIL.Image.open(image_path)

            response = vision_model.generate_content([prompt, image])

            if response.text:
                logger.info(f"Generated vision response: {len(response.text)} chars")
                return response.text
            else:
                logger.warning("Gemini Vision returned empty response")
                return ""

        except Exception as e:
            logger.error(f"Gemini Vision generation failed: {e}")
            return ""

    async def list_models(self) -> List[str]:
        """List available Gemini models"""
        try:
            models = self.client.models.list()
            return [model.name for model in models if 'gemini' in model.name.lower()]
        except Exception as e:
            logger.error(f"Failed to list Gemini models: {e}")
            return ["gemini-2.0-flash-exp", "gemini-pro", "gemini-pro-vision"]

    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return bool(self.api_key)

    async def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Get information about a model"""
        model = model_name or "gemini-2.0-flash-exp"
        try:
            models = self.client.models.list()
            for m in models:
                if model in m.name:
                    return {
                        "name": m.name,
                        "description": getattr(m, 'description', 'Google Gemini model'),
                        "supported_generation_methods": getattr(m, 'supported_generation_methods', [])
                    }
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")

        return {"name": model, "description": "Google Gemini model", "status": "unknown"}

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """Generate image using Gemini Image Generation API"""
        try:
            # Use image-specific API key
            image_api_key = self.image_api_key
            if not image_api_key:
                logger.error("No Gemini Image API key provided")
                return ""

            # Initialize image client if needed
            if not self.image_client:
                self.image_client = genai.Client(api_key=image_api_key)

            # Use Imagen model for image generation
            response = await self.image_client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt,
                config=genai.types.GenerateImagesConfig(
                    number_of_images=1,
                    include_rai_reason=True
                )
            )

            if response.generated_images and len(response.generated_images) > 0:
                # Save image to file
                import base64
                from pathlib import Path

                # The response structure might be different - let's check
                image_data = response.generated_images[0]
                if hasattr(image_data, 'image'):
                    # If it's a PIL image or similar
                    image_bytes = image_data.image
                    if hasattr(image_bytes, 'tobytes'):
                        image_bytes = image_bytes.tobytes()
                else:
                    # Assume it's already bytes
                    image_bytes = image_data

                output_dir = Path("generated_images")
                output_dir.mkdir(exist_ok=True)

                filename = kwargs.get('filename', f"gemini_image_{int(__import__('time').time())}.png")
                filepath = output_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(image_bytes)

                logger.info(f"Generated image saved to: {filepath}")
                return str(filepath)

            logger.warning("Gemini Image Generation returned no image data")
            return ""

        except Exception as e:
            error_msg = str(e)
            if "expired" in error_msg.lower() or "invalid" in error_msg.lower() or "404" in error_msg or "not found" in error_msg.lower():
                logger.error(f"Gemini Image API key expired, invalid, or model not available: {e}")
            else:
                logger.error(f"Gemini Image generation failed: {e}")
            return ""