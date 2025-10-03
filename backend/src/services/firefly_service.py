"""
Adobe Firefly integration service for generating creative assets.
"""
import os
import uuid
import httpx
from pathlib import Path
from typing import Optional, List, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session


class FireflyService:
    """Handles Adobe Firefly API integration for creative generation"""
    
    def __init__(self):
        self.api_key = os.getenv("FIREFLY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = os.getenv("FIREFLY_API_URL", "https://firefly-api.adobe.io/v2/images/generate")
        self.timeout = 30.0
        self.output_dir = Path("uploads/creatives")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def _get_adobe_access_token(self, db: Session) -> Optional[str]:
        """Generate Adobe access token from client credentials"""
        from .key_service import key_service
        
        client_id = key_service.get_value(db, "adobe_client_id")
        client_secret = key_service.get_value(db, "adobe_client_secret")
        
        if not client_id or not client_secret:
            print("Missing Adobe client_id or client_secret")
            return None
        
        print(f"Generating Adobe access token with client_id: {client_id}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://ims-na1.adobelogin.com/ims/token/v3",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "scope": "openid,AdobeID,session,additional_info,read_organizations,firefly_api,ff_apis"
                    }
                )
                
                print(f"Adobe IMS response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get("access_token")
                    expires_in = data.get("expires_in")
                    print(f"✅ Got access token, expires in {expires_in} seconds")
                    return access_token
                else:
                    print(f"❌ Adobe IMS error: {response.text}")
                    return None
        except Exception as e:
            print(f"❌ Error getting Adobe access token: {e}")
            return None
    
    def _get_provider_config(self, db: Session):
        """Get image provider and API key from settings"""
        from .key_service import key_service
        
        # Get provider name from use_image_model key
        provider = key_service.get_value(db, "use_image_model") or key_service.get_value(db, "image_provider") or "Adobe Firefly"
        
        # For Adobe Firefly, we'll generate the access token on-demand
        # For all others, get API key using provider name as the key in the keys table
        if provider == "Adobe Firefly":
            api_key = "GENERATE_ON_DEMAND"  # Placeholder, will be replaced
        else:
            # Look up the API key using the provider name as the key
            # e.g., if provider is "DALL-E", look up key="DALL-E" in keys table
            api_key = key_service.get_value(db, provider)
        
        # Map provider to API URL
        provider_configs = {
            "Adobe Firefly": "https://firefly-api.adobe.io/v3/images/generate",
            "Midjourney": "https://api.midjourney.com/v1/imagine",
            "DALL-E": "https://api.openai.com/v1/images/generations",
            "OpenAI": "https://api.openai.com/v1/images/generations",
            "Stable Diffusion": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            "Freepik": "https://api.freepik.com/v1/ai/text-to-image"
        }
        
        api_url = provider_configs.get(provider, provider_configs["Adobe Firefly"])
        return api_key, api_url, provider
    
    async def generate_creative(
        self,
        db: Session,
        idea_content: str,
        campaign_message: str,
        region: str,
        demographic: str,
        aspect_ratio: str = "1:1",
        brand_colors: Optional[List[str]] = None,
        language_code: str = "en-US",
        brand_name: str = None,
        brand_logo_path: str = None
    ) -> Tuple[str, str, int, Optional[str]]:
        """
        Generate creative asset using Adobe Firefly.
        
        Args:
            idea_content: Creative idea text
            campaign_message: Campaign message to include
            region: Target region
            demographic: Target demographic
            brand_colors: Optional list of brand colors (hex codes)
            brand_logo_path: Optional path to brand logo for compositing
        
        Returns:
            Tuple of (file_path, mime_type, file_size, firefly_job_id)
        
        Raises:
            HTTPException: If generation fails
        """
        # Get provider config from settings
        api_key, api_url, provider = self._get_provider_config(db)
        
        print(f"\n{'='*80}")
        print(f"🎨 IMAGE GENERATION REQUEST")
        print(f"{'='*80}")
        print(f"Provider: {provider}")
        print(f"API URL: {api_url}")
        print(f"API Key Present: {bool(api_key)}")
        print(f"API Key Length: {len(api_key) if api_key else 0}")
        print(f"Aspect Ratio: {aspect_ratio}")
        print(f"Region: {region}")
        print(f"Demographic: {demographic}")
        if api_key and len(api_key) > 50:
            print(f"API Key Preview: {api_key[:20]}...{api_key[-10:]}")
        elif api_key:
            print(f"API Key: {api_key}")
        print(f"{'='*80}\n")
        
        # Build prompt for Firefly
        prompt = self._build_firefly_prompt(
            idea_content, campaign_message, region, demographic, brand_colors, language_code, brand_name
        )
        
        # Store campaign message, language, and brand info for text overlay
        self._temp_campaign_message = campaign_message
        self._temp_language_code = language_code
        self._temp_brand_name = brand_name
        self._temp_brand_logo_path = brand_logo_path
        
        # For Adobe Firefly, generate access token on-demand
        if provider == "Adobe Firefly" and api_key == "GENERATE_ON_DEMAND":
            print("🔑 Generating Adobe access token...")
            api_key = await self._get_adobe_access_token(db)
            if not api_key:
                print("❌ Using MOCK: Failed to generate Adobe access token")
                file_path, file_size = self._create_mock_creative(prompt, aspect_ratio)
                return file_path, "image/jpeg", file_size, None
        
        # Call Firefly API (mock if no API key or if API fails)
        if not api_key or api_key.strip() == "" or api_key == "your_firefly_api_key_here":
            # Mock creative generation for development
            print(f"\n{'='*80}")
            print(f"⚠️  NO API KEY CONFIGURED - USING MOCK IMAGE")
            print(f"{'='*80}")
            print(f"Provider: {provider}")
            print(f"Reason: API key is empty or placeholder")
            print(f"Action: Generating mock creative image")
            print(f"{'='*80}\n")
            file_path, file_size = self._create_mock_creative(prompt, aspect_ratio)
            return file_path, "image/jpeg", file_size, None
        else:
            try:
                print(f"🚀 Calling {provider} API...")
                result = await self._call_firefly_api(
                    prompt, aspect_ratio, api_key, api_url, provider, db,
                    campaign_message=self._temp_campaign_message,
                    language_code=self._temp_language_code,
                    brand_name=self._temp_brand_name,
                    brand_logo_path=self._temp_brand_logo_path
                )
                return result
            except Exception as e:
                # Fall back to mock if API fails (403, invalid key, etc.)
                print(f"\n{'='*80}")
                print(f"❌ API CALL FAILED - FALLING BACK TO MOCK IMAGE")
                print(f"{'='*80}")
                print(f"Provider: {provider}")
                print(f"Error: {str(e)}")
                import traceback
                print(f"Traceback:\n{traceback.format_exc()}")
                print(f"Action: Generating mock creative image")
                print(f"{'='*80}\n")
                file_path, file_size = self._create_mock_creative(prompt, aspect_ratio)
                return file_path, "image/jpeg", file_size, None
    
    def _build_firefly_prompt(
        self, 
        idea_content: str, 
        campaign_message: str, 
        region: str, 
        demographic: str, 
        brand_colors: Optional[List[str]] = None,
        language_code: str = "en-US",
        brand_name: str = None
    ) -> str:
        """Build prompt for Firefly API with logo and text overlay requirements"""
        color_info = ""
        if brand_colors:
            color_info = f"\nUse brand colors: {', '.join(brand_colors)}"
        
        # Language for text overlay
        language_instruction = f"\nText language: {language_code.split('-')[0].upper()}"
        
        # Logo instruction
        logo_instruction = ""
        if brand_name:
            logo_instruction = f"\nInclude a professional logo in the corner with brand name '{brand_name}'"
        else:
            logo_instruction = "\nInclude a simple, elegant brand logo in the corner"
        
        prompt = f"""Professional social media creative image: {idea_content}

REQUIRED TEXT OVERLAY:
- Campaign message: "{campaign_message}"
- Make the text prominent, readable, and professionally styled
- Position text overlay strategically on the image{language_instruction}
{logo_instruction}
Target audience: {demographic} in {region}{color_info}

Style: High quality, professional marketing imagery with clear text overlay and branding elements."""
        
        return prompt
    
    async def _call_firefly_api(self, prompt: str, aspect_ratio: str, api_key: str, api_url: str, provider: str, db: Session = None, campaign_message: str = None, language_code: str = "en-US", brand_name: str = None, brand_logo_path: str = None) -> Tuple[str, str, int, str]:
        """Call image generation API and add text overlays"""
        from .key_service import key_service
        
        # Set headers based on provider
        if provider == "Freepik":
            headers = {
                "x-freepik-api-key": api_key,
                "Content-Type": "application/json"
            }
        elif provider == "Adobe Firefly":
            # For Adobe Firefly, x-api-key should be the client_id, not the JWT
            client_id = key_service.get_value(db, "adobe_client_id")
            print(f"Using Adobe client_id for x-api-key: {client_id}")
            headers = {
                "Authorization": f"Bearer {api_key[:50]}...",
                "Content-Type": "application/json",
                "x-api-key": client_id if client_id else api_key
            }
        else:
            # Default for other providers
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        
        print(f"Request headers: {headers}")
        
        # Determine dimensions based on aspect ratio
        dimensions = self._get_dimensions(aspect_ratio)
        
        # Build payload based on provider
        if provider in ["OpenAI", "DALL-E"]:
            # OpenAI DALL-E format
            size_map = {
                "16:9": "1792x1024",  # DALL-E 3 landscape
                "9:16": "1024x1792",  # DALL-E 3 portrait
                "1:1": "1024x1024"    # DALL-E 3 square
            }
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": size_map.get(aspect_ratio, "1024x1024"),
                "quality": "standard",
                "response_format": "b64_json"  # Get base64 instead of URL to avoid Azure blob auth issues
            }
        elif provider == "Freepik":
            # Freepik format
            payload = {
                "prompt": prompt,
                "size": dimensions,
                "contentClass": "photo"
            }
        else:
            # Adobe Firefly and others
            payload = {
                "prompt": prompt,
                "size": dimensions,
                "contentClass": "photo",
                "style": {
                    "presets": ["professional", "vibrant"]
                }
            }
        
        try:
            print(f"Making POST request to: {api_url}")
            print(f"Payload: {payload}")
            
            # Use longer timeout for base64 responses (DALL-E, Freepik)
            # Base64 image data can be several MB and takes longer to transmit
            timeout = 120.0 if provider in ["OpenAI", "DALL-E", "Freepik"] else self.timeout
            print(f"Using timeout: {timeout}s")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(api_url, json=payload, headers=headers)
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
                
                # Check for quota/rate limit errors BEFORE raising
                if response.status_code == 429:
                    print("\n" + "="*80)
                    print("🚨 QUOTA/RATE LIMIT EXCEEDED 🚨")
                    print("="*80)
                    print(f"Provider: {provider}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    print("="*80 + "\n")
                    raise HTTPException(
                        status_code=429,
                        detail=f"Image API quota/rate limit exceeded for {provider}. Please wait or check your API limits."
                    )
                
                if response.status_code == 403:
                    print("\n" + "="*80)
                    print("🚨 API ACCESS FORBIDDEN 🚨")
                    print("="*80)
                    print(f"Provider: {provider}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    print("Possible reasons:")
                    print("  - Invalid API key")
                    print("  - Quota exceeded")
                    print("  - Insufficient permissions")
                    print("="*80 + "\n")
                
                if response.status_code >= 400:
                    print("\n" + "="*80)
                    print(f"🚨 IMAGE API ERROR: {response.status_code} 🚨")
                    print("="*80)
                    print(f"Provider: {provider}")
                    print(f"URL: {api_url}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    print("="*80 + "\n")
                
                response.raise_for_status()
                
                data = response.json()
                print(f"Response data keys: {data.keys()}")
                
                # Handle different response formats
                if provider == "Freepik":
                    # Freepik returns base64 directly
                    import base64
                    job_id = None
                    base64_data = data["data"][0]["base64"]
                    image_content = base64.b64decode(base64_data)
                    print(f"Decoded {len(image_content)} bytes from base64")
                elif provider in ["OpenAI", "DALL-E"]:
                    # OpenAI DALL-E returns base64 data directly
                    import base64
                    job_id = None
                    base64_data = data["data"][0]["b64_json"]
                    
                    print(f"Decoding base64 image data...")
                    
                    image_content = base64.b64decode(base64_data)
                    
                    if len(image_content) == 0:
                        print(f"❌ Decoded image is empty!")
                        raise HTTPException(
                            status_code=500,
                            detail="Decoded image from DALL-E is empty"
                        )
                    
                    print(f"✅ Decoded {len(image_content)} bytes from base64")
                    
                    # Verify it's a valid image format
                    if not image_content.startswith(b'\xff\xd8\xff') and not image_content.startswith(b'\x89PNG'):
                        print(f"❌ Decoded content is not a valid image!")
                        print(f"Content preview: {image_content[:100]}")
                        raise HTTPException(
                            status_code=500,
                            detail="Decoded content from DALL-E is not a valid image"
                        )
                else:
                    # Adobe Firefly and others return URL in outputs
                    job_id = data.get("id")
                    image_url = data["outputs"][0]["image"]["url"]
                    
                    print(f"Downloading image from: {image_url}")
                    
                    # Download generated image
                    image_response = await client.get(image_url)
                    image_content = image_response.content
                    
                    print(f"Downloaded {len(image_content)} bytes")
                
                # Save initial image to temporary file
                temp_filename = f"{uuid.uuid4()}_temp.jpg"
                temp_file_path = self.output_dir / temp_filename
                
                with open(temp_file_path, "wb") as f:
                    f.write(image_content)
                
                print(f"Saved base image to: {temp_file_path}")
                
                # Add text overlays (campaign message and brand logo text)
                final_filename = f"{uuid.uuid4()}.jpg"
                final_file_path = self.output_dir / final_filename
                
                dimensions = self._get_dimensions(aspect_ratio)
                self._add_text_overlays(
                    str(temp_file_path),
                    str(final_file_path),
                    campaign_message,
                    language_code,
                    brand_name,
                    dimensions["width"],
                    dimensions["height"],
                    brand_logo_path
                )
                
                # Delete temp file
                temp_file_path.unlink()
                
                # Get final file size
                final_file_size = final_file_path.stat().st_size
                
                print(f"\n{'='*80}")
                print(f"✅ IMAGE GENERATION SUCCESS!")
                print(f"{'='*80}")
                print(f"Provider: {provider}")
                print(f"File Path: {final_file_path}")
                print(f"File Size: {final_file_size} bytes")
                print(f"Job ID: {job_id}")
                print(f"{'='*80}\n")
                
                return str(final_file_path), "image/jpeg", final_file_size, job_id
        
        except httpx.HTTPError as e:
            print("\n" + "="*80)
            print("🚨 IMAGE GENERATION HTTP ERROR 🚨")
            print("="*80)
            print(f"Provider: {provider}")
            print(f"Error: {e}")
            if hasattr(e, 'response'):
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Text: {e.response.text}")
                print(f"Response Headers: {e.response.headers}")
            else:
                print("No response available")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=500,
                detail=f"Image API error ({provider}): {str(e)}"
            )
        except Exception as e:
            print("\n" + "="*80)
            print("🚨 UNEXPECTED IMAGE GENERATION ERROR 🚨")
            print("="*80)
            print(f"Provider: {provider}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error in image generation ({provider}): {str(e)}"
            )
    
    def _add_text_overlays(
        self,
        input_path: str,
        output_path: str,
        campaign_message: str,
        language_code: str,
        brand_name: str,
        width: int,
        height: int,
        brand_logo_path: str = None
    ):
        """Add text overlays and brand logo to the generated image"""
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        # If no campaign message, just copy the file (for brand/product assets)
        if not campaign_message:
            import shutil
            shutil.copy(input_path, output_path)
            print(f"✅ No text overlay needed (brand/product asset)")
            return
        
        # Translate campaign message to appropriate language
        translated_message = self._translate_campaign_message(campaign_message, language_code)
        
        # Open the image
        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts
        try:
            # Campaign message font (large)
            message_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.06))
            # Brand name font (medium)
            brand_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.04))
        except:
            message_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()
        
        # Add semi-transparent background for campaign message
        message_lines = textwrap.wrap(translated_message, width=30)
        message_text = "\n".join(message_lines)
        
        # Calculate text bounding box for campaign message
        bbox = draw.textbbox((0, 0), message_text, font=message_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position at bottom center
        message_x = (width - text_width) // 2
        message_y = height - text_height - int(height * 0.1)
        
        # Draw semi-transparent background
        padding = int(height * 0.03)
        draw.rectangle(
            [message_x - padding, message_y - padding,
             message_x + text_width + padding, message_y + text_height + padding],
            fill=(0, 0, 0, 180)
        )
        
        # Draw campaign message text
        draw.text((message_x, message_y), message_text, fill="white", font=message_font, align="center")
        
        # Add brand name in top-right corner
        if brand_name:
            brand_text = brand_name.upper()
            brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
            brand_width = brand_bbox[2] - brand_bbox[0]
            brand_x = width - brand_width - int(width * 0.05)
            brand_y = int(height * 0.05)
            
            # Draw semi-transparent background for brand
            brand_padding = int(height * 0.02)
            draw.rectangle(
                [brand_x - brand_padding, brand_y - brand_padding,
                 brand_x + brand_width + brand_padding, brand_y + (brand_bbox[3] - brand_bbox[1]) + brand_padding],
                fill=(255, 255, 255, 200)
            )
            
            # Draw brand name
            draw.text((brand_x, brand_y), brand_text, fill="black", font=brand_font)
        
        # Composite brand logo if provided
        if brand_logo_path:
            try:
                import os
                if os.path.exists(brand_logo_path):
                    logo = Image.open(brand_logo_path)
                    
                    # Resize logo to appropriate size (max 15% of image width/height)
                    max_logo_size = int(min(width, height) * 0.15)
                    logo.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
                    
                    # Position logo in top-left corner with padding
                    logo_x = int(width * 0.05)
                    logo_y = int(height * 0.05)
                    
                    # Handle transparency
                    if logo.mode in ('RGBA', 'LA'):
                        # Create a white background
                        background = Image.new('RGB', logo.size, (255, 255, 255))
                        background.paste(logo, mask=logo.split()[-1] if logo.mode == 'RGBA' else None)
                        img.paste(background, (logo_x, logo_y))
                    else:
                        img.paste(logo, (logo_x, logo_y))
                    
                    print(f"✅ Composited brand logo from: {brand_logo_path}")
            except Exception as e:
                print(f"⚠️ Failed to composite logo: {e}")
        
        # Save the image
        img.save(output_path, 'JPEG', quality=95)
        print(f"✅ Added text overlays: '{translated_message}' + brand '{brand_name}'")
    
    def _translate_campaign_message(self, message: str, language_code: str) -> str:
        """
        Translate campaign message to appropriate language using Google Translate.
        """
        import httpx
        
        lang = language_code.split('-')[0].lower()
        
        if lang == "en":
            return message
        
        # Language code mapping
        lang_map = {
            "ja": "ja",  # Japanese
            "zh": "zh-CN",  # Chinese Simplified
            "ko": "ko",  # Korean
            "de": "de",  # German
            "fr": "fr",  # French
            "es": "es",  # Spanish
            "it": "it",  # Italian
            "pt": "pt",  # Portuguese
        }
        
        target_lang = lang_map.get(lang, lang)
        
        try:
            # Use Google Translate API (free tier)
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "en",
                "tl": target_lang,
                "dt": "t",
                "q": message
            }
            
            response = httpx.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                result = response.json()
                translated = result[0][0][0]
                print(f"🌍 Translated '{message}' to {target_lang}: '{translated}'")
                return translated
        except Exception as e:
            print(f"⚠️ Translation failed: {e}, using original message")
        
        return message
    
    def _get_dimensions(self, aspect_ratio: str) -> dict:
        """Get image dimensions for aspect ratio"""
        dimensions_map = {
            "16:9": {"width": 1920, "height": 1080},
            "9:16": {"width": 1080, "height": 1920},
            "1:1": {"width": 1080, "height": 1080}
        }
        return dimensions_map.get(aspect_ratio, {"width": 1080, "height": 1080})
    
    def _create_mock_creative(self, prompt: str, aspect_ratio: str) -> Tuple[str, int]:
        """Create mock creative for development (simple image file)"""
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        # Create a simple placeholder image file
        filename = f"{uuid.uuid4()}.jpg"
        file_path = self.output_dir / filename
        
        # Get dimensions for aspect ratio
        dimensions = self._get_dimensions(aspect_ratio)
        width = dimensions["width"]
        height = dimensions["height"]
        
        # Create image with gradient background
        img = Image.new('RGB', (width, height), color='#4A5568')
        draw = ImageDraw.Draw(img)
        
        # Add text overlay
        text = f"MOCK CREATIVE\n{aspect_ratio}\n\n{prompt[:100]}..."
        
        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Add aspect ratio text at top
        draw.text((width//2, 60), f"MOCK: {aspect_ratio}", fill='white', font=font, anchor='mm')
        
        # Add wrapped prompt text
        wrapped_text = textwrap.fill(prompt[:200], width=40)
        draw.text((width//2, height//2), wrapped_text, fill='#E2E8F0', font=small_font, anchor='mm', align='center')
        
        # Save image
        img.save(file_path, 'JPEG', quality=85)
        file_size = file_path.stat().st_size
        
        return str(file_path), file_size


# Singleton instance
firefly_service = FireflyService()
