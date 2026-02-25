"""
ImageAgent — Generates images using FLUX.1-schnell via HuggingFace Inference API.
Uses Gemini to create optimized image prompts, uploads results to Supabase Storage.
"""

import io
import uuid
from datetime import datetime, timezone
from typing import Optional

import google.generativeai as genai
import requests
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import get_settings
from core.supabase import get_supabase_client

logger = structlog.get_logger()

# HuggingFace model endpoints
FLUX_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
SDXL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


class ImageAgent:
    def __init__(self):
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.gemini = genai.GenerativeModel("gemini-2.0-flash")
        self.hf_headers = {"Authorization": f"Bearer {self.settings.hf_token}"}

    async def run(
        self,
        caption: str,
        brand_data: dict,
        platform: str,
    ) -> Optional[str]:
        """
        Generate an image for a post:
        1. Create optimized FLUX prompt using Gemini
        2. Generate image via HuggingFace FLUX.1-schnell
        3. Upload to Supabase Storage
        4. Return public URL
        """
        if not self.settings.hf_token:
            logger.warning("No HF token configured, skipping image generation")
            return None

        try:
            # Step 1: Generate optimized prompt
            image_prompt = await self._create_image_prompt(caption, brand_data, platform)
            logger.info("Image prompt generated", prompt=image_prompt[:100])

            # Step 2: Generate image
            image_bytes = await self._generate_image(image_prompt)
            if not image_bytes:
                return None

            # Step 3: Upload to Supabase Storage
            url = self._upload_to_storage(image_bytes, brand_data["id"])
            logger.info("Image uploaded", url=url)

            return url

        except Exception as e:
            logger.error("Image generation pipeline failed", error=str(e))
            return None

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=8))
    async def _create_image_prompt(
        self,
        caption: str,
        brand_data: dict,
        platform: str,
    ) -> str:
        """Use Gemini to create an optimized FLUX image prompt."""
        platform_sizes = {
            "linkedin": "landscape orientation, 1200x627 aspect ratio",
            "instagram": "square composition, 1080x1080 aspect ratio",
            "twitter": "landscape orientation, 1600x900 aspect ratio",
        }

        prompt = f"""Create an image generation prompt for FLUX.1 AI model to accompany this social media post.

POST CAPTION:
{caption[:500]}

BRAND: {brand_data.get('name', 'Unknown')}
NICHE: {brand_data.get('niche', '')}
PLATFORM: {platform}
COMPOSITION: {platform_sizes.get(platform, 'landscape')}

RULES:
- Photorealistic or clean 3D render style
- NO text overlays in the image
- NO human faces (use silhouettes, backs of heads, or abstract figures)
- Modern, professional aesthetic
- Bold, clean compositions with strong visual hierarchy
- Use brand-appropriate color palette
- Think "premium tech blog hero image" or "startup pitch deck visual"

Return ONLY the image prompt, no explanation. Keep it under 100 words."""

        response = self.gemini.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=200,
            ),
        )

        return response.text.strip().strip('"')

    async def _generate_image(self, prompt: str) -> Optional[bytes]:
        """Generate image using HuggingFace FLUX.1-schnell with SDXL fallback."""
        # Try FLUX first
        image_bytes = self._call_hf_model(FLUX_URL, prompt)
        if image_bytes:
            return image_bytes

        logger.warning("FLUX failed, trying SDXL fallback")
        # Fallback to SDXL
        image_bytes = self._call_hf_model(SDXL_URL, prompt)
        if image_bytes:
            return image_bytes

        logger.error("All image models failed")
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=3, max=30))
    def _call_hf_model(self, model_url: str, prompt: str) -> Optional[bytes]:
        """Call HuggingFace Inference API for image generation."""
        try:
            response = requests.post(
                model_url,
                headers=self.hf_headers,
                json={"inputs": prompt},
                timeout=self.settings.hf_request_timeout,
            )

            if response.status_code == 200:
                # Verify it's actually an image
                content_type = response.headers.get("content-type", "")
                if "image" in content_type or len(response.content) > 1000:
                    return response.content
                logger.warning("Response not an image", content_type=content_type)
                return None

            if response.status_code == 503:
                # Model loading, retry
                logger.info("Model loading, will retry", url=model_url)
                raise Exception("Model is loading")

            if response.status_code == 429:
                logger.warning("Rate limited by HuggingFace", url=model_url)
                return None

            logger.error(
                "HuggingFace API error",
                status=response.status_code,
                body=response.text[:200],
            )
            return None

        except requests.exceptions.Timeout:
            logger.warning("HuggingFace request timed out", url=model_url)
            return None

    def _upload_to_storage(self, image_bytes: bytes, brand_id: str) -> str:
        """Upload image to Supabase Storage and return public URL."""
        supabase = get_supabase_client()

        filename = f"{brand_id}/{uuid.uuid4().hex}.png"

        # Upload
        supabase.storage.from_("post-images").upload(
            filename,
            image_bytes,
            file_options={"content-type": "image/png", "upsert": "true"},
        )

        # Get public URL
        url = supabase.storage.from_("post-images").get_public_url(filename)
        return url
