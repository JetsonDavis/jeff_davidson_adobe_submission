"""
LLM integration service for generating creative ideas.
"""
import os
import httpx
from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session


class LLMService:
    """Handles LLM API integration for idea generation"""
    
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
        self.model = os.getenv("LLM_MODEL", "gpt-4")
        self.timeout = 30.0
    
    def _get_provider_config(self, db: Session):
        """Get LLM provider and API key from settings"""
        from .key_service import key_service
        
        # Check use_llm first, then fall back to llm_provider
        provider = key_service.get_value(db, "use_llm") or key_service.get_value(db, "llm_provider") or "OpenAI"
        
        # Get API key using provider name as key
        api_key = key_service.get_value(db, provider) or self.api_key
        
        # Map provider to API URL and model
        provider_configs = {
            "OpenAI": {
                "url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-4"
            },
            "Anthropic": {
                "url": "https://api.anthropic.com/v1/messages",
                "model": "claude-3-opus-20240229"
            },
            "Gemini": {
                "url": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
                "model": "gemini-pro"
            },
            "Grok": {
                "url": "https://api.x.ai/v1/chat/completions",
                "model": "grok-beta"
            },
            "DeepSeek": {
                "url": "https://api.deepseek.com/v1/chat/completions",
                "model": "deepseek-chat"
            }
        }
        
        config = provider_configs.get(provider, provider_configs["OpenAI"])
        return api_key, config["url"], config["model"]
    
    async def generate_ideas(
        self,
        db: Session,
        brief_content: str,
        campaign_message: str,
        regions: List[str],
        demographics: List[str]
    ) -> List[Dict[str, str]]:
        """
        Generate creative ideas for each region/demographic combination.
        
        Args:
            brief_content: Product brief text
            campaign_message: Campaign message to incorporate
            regions: List of target regions
            demographics: List of target demographics
        
        Returns:
            List of dicts with keys: region, demographic, content, language_code
        
        Raises:
            HTTPException: If LLM generation fails
        """
        ideas = []
        
        # Get provider config from settings
        api_key, api_url, model = self._get_provider_config(db)
        
        # Get provider name for logging
        from .key_service import key_service
        provider = key_service.get_value(db, "use_llm") or key_service.get_value(db, "llm_provider") or "OpenAI"
        
        print(f"\n{'='*60}")
        print(f">>> USING LLM: {provider.upper()} (MODEL: {model.upper()}) <<<")
        print(f"{'='*60}\n")
        
        # Generate one idea per region/demographic combination
        for region in regions:
            for demographic in demographics:
                idea = await self._generate_single_idea(
                    db, brief_content, campaign_message, region, demographic, 
                    api_key, api_url, model
                )
                ideas.append(idea)
        
        return ideas
    
    async def _generate_single_idea(
        self,
        db: Session,
        brief_content: str,
        campaign_message: str,
        region: str,
        demographic: str,
        api_key: str,
        api_url: str,
        model: str
    ) -> Dict[str, str]:
        """Generate a single creative idea for specific region/demographic"""
        
        # Determine language based on region
        language_code = self._get_language_for_region(region)
        
        # Construct prompt
        prompt = self._build_prompt(brief_content, campaign_message, region, demographic)
        
        # Call LLM API (mock if no API key)
        if not api_key or api_key.strip() == "" or api_key == "your_llm_api_key_here":
            # Mock response for development - in the target language
            print(f"\n{'='*80}")
            print(f"⚠️  NO LLM API KEY CONFIGURED - USING MOCK IDEA")
            print(f"{'='*80}")
            print(f"Region: {region}")
            print(f"Demographic: {demographic}")
            print(f"Language: {language_code}")
            print(f"Reason: API key is empty or placeholder")
            print(f"Action: Generating mock creative idea")
            print(f"{'='*80}\n")
            content = self._get_mock_idea(region, demographic, campaign_message, language_code)
        else:
            # Use actual LLM API
            content = await self._call_llm_api(prompt, api_key, api_url, model)
        
        return {
            "region": region,
            "demographic": demographic,
            "content": content,
            "language_code": language_code
        }
    
    def _get_mock_idea(self, region: str, demographic: str, campaign_message: str, language_code: str) -> str:
        """Generate mock idea in appropriate language"""
        mock_templates = {
            "en-US": f"[MOCK] Creative social media idea for {demographic} in {region}: Showcase product features with lifestyle imagery emphasizing {campaign_message}. Focus on regional preferences and demographic interests.",
            "en-GB": f"[MOCK] Creative social media idea for {demographic} in {region}: Showcase product features with lifestyle imagery emphasising {campaign_message}. Focus on regional preferences and demographic interests.",
            "es-MX": f"[MOCK] Idea creativa para redes sociales dirigida a {demographic} en {region}: Muestra las características del producto con imágenes de estilo de vida que enfatizan {campaign_message}. Enfócate en preferencias regionales e intereses demográficos.",
            "es-ES": f"[MOCK] Idea creativa para redes sociales dirigida a {demographic} en {region}: Muestra las características del producto con imágenes de estilo de vida que enfatizan {campaign_message}. Enfócate en preferencias regionales e intereses demográficos.",
            "fr-FR": f"[MOCK] Idée créative pour les réseaux sociaux pour {demographic} en {region}: Présentez les fonctionnalités du produit avec des images de style de vie mettant l'accent sur {campaign_message}. Concentrez-vous sur les préférences régionales et les intérêts démographiques.",
            "de-DE": f"[MOCK] Kreative Social-Media-Idee für {demographic} in {region}: Zeigen Sie Produktfunktionen mit Lifestyle-Bildern, die {campaign_message} betonen. Konzentrieren Sie sich auf regionale Präferenzen und demografische Interessen.",
            "ja-JP": f"[MOCK] {region}の{demographic}向けのクリエイティブなソーシャルメディアのアイデア：{campaign_message}を強調したライフスタイル画像で製品の特徴を紹介します。地域の好みや人口統計の興味に焦点を当てます。",
            "zh-CN": f"[MOCK] 面向{region}{demographic}的创意社交媒体想法：通过强调{campaign_message}的生活方式图像展示产品功能。关注区域偏好和人口统计兴趣。",
            "ko-KR": f"[MOCK] {region}의 {demographic}를 위한 창의적인 소셜 미디어 아이디어: {campaign_message}를 강조하는 라이프스타일 이미지로 제품 기능을 선보이세요. 지역 선호도와 인구 통계적 관심사에 초점을 맞춥니다.",
            "it-IT": f"[MOCK] Idea creativa per i social media per {demographic} in {region}: Mostra le caratteristiche del prodotto con immagini di lifestyle che enfatizzano {campaign_message}. Concentrati sulle preferenze regionali e sugli interessi demografici.",
            "pt-BR": f"[MOCK] Ideia criativa para redes sociais para {demographic} em {region}: Mostre recursos do produto com imagens de estilo de vida enfatizando {campaign_message}. Concentre-se em preferências regionais e interesses demográficos."
        }
        
        return mock_templates.get(language_code, mock_templates["en-US"])
    
    def _build_prompt(
        self,
        brief_content: str,
        campaign_message: str,
        region: str,
        demographic: str
    ) -> str:
        """Build prompt for LLM with language-specific instructions"""
        
        # Get language for the region
        language_code = self._get_language_for_region(region)
        
        # Map language codes to language names and instructions
        language_instructions = {
            "en-US": ("English", ""),
            "en-GB": ("English", ""),
            "en-EU": ("English", ""),
            "en-APAC": ("English", ""),
            "es-MX": ("Spanish", "IMPORTANT: Write the creative idea entirely in Spanish."),
            "es-ES": ("Spanish", "IMPORTANT: Write the creative idea entirely in Spanish."),
            "fr-FR": ("French", "IMPORTANT: Write the creative idea entirely in French."),
            "de-DE": ("German", "IMPORTANT: Write the creative idea entirely in German."),
            "ja-JP": ("Japanese", "IMPORTANT: Write the creative idea entirely in Japanese."),
            "zh-CN": ("Chinese", "IMPORTANT: Write the creative idea entirely in Simplified Chinese."),
            "ko-KR": ("Korean", "IMPORTANT: Write the creative idea entirely in Korean."),
            "it-IT": ("Italian", "IMPORTANT: Write the creative idea entirely in Italian."),
            "pt-BR": ("Portuguese", "IMPORTANT: Write the creative idea entirely in Portuguese.")
        }
        
        language_name, language_instruction = language_instructions.get(
            language_code, 
            ("English", "")
        )
        
        return f"""You are a creative social media marketing strategist. Generate a compelling creative idea for a social media campaign.

Product Brief:
{brief_content}

Campaign Message: {campaign_message}
Target Region: {region}
Target Demographic: {demographic}
Target Language: {language_name}

{language_instruction}

Generate a creative concept that:
1. Resonates with the target demographic in this region
2. Incorporates the campaign message naturally
3. Is suitable for social media platforms (Instagram, Facebook, Twitter)
4. Considers regional cultural preferences and language
5. Is concise and actionable (2-3 sentences)
6. Is written in {language_name} to match the target audience

Creative Idea:"""
    
    async def _call_llm_api(self, prompt: str, api_key: str, api_url: str, model: str) -> str:
        """Call LLM API to generate content"""
        # Determine provider from model/url
        provider = "Unknown"
        if "openai" in api_url:
            provider = "OpenAI"
        elif "anthropic" in api_url:
            provider = "Anthropic"
        elif "x.ai" in api_url:
            provider = "Grok"
        elif "deepseek" in api_url:
            provider = "DeepSeek"
        elif "generativelanguage.googleapis.com" in api_url:
            provider = "Gemini"
        
        print(f"\n{'='*80}")
        print(f"🤖 LLM API REQUEST")
        print(f"{'='*80}")
        print(f"Provider: {provider}")
        print(f"Model: {model}")
        print(f"API URL: {api_url}")
        print(f"API Key Present: {bool(api_key)}")
        print(f"API Key Length: {len(api_key) if api_key else 0}")
        if api_key and len(api_key) > 50:
            print(f"API Key Preview: {api_key[:20]}...{api_key[-10:]}")
        elif api_key:
            print(f"API Key: {api_key}")
        print(f"{'='*80}\n")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a creative social media marketing strategist."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.8
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(api_url, json=payload, headers=headers)
                
                print(f"LLM Response status: {response.status_code}")
                
                # Check for quota/rate limit errors BEFORE raising
                if response.status_code == 429:
                    print("\n" + "="*80)
                    print("🚨 LLM QUOTA/RATE LIMIT EXCEEDED 🚨")
                    print("="*80)
                    print(f"Provider: {provider}")
                    print(f"Model: {model}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    print("="*80 + "\n")
                    raise HTTPException(
                        status_code=429,
                        detail=f"LLM API quota/rate limit exceeded for {provider}. Please wait or check your API limits."
                    )
                
                if response.status_code == 403:
                    print("\n" + "="*80)
                    print("🚨 LLM API ACCESS FORBIDDEN 🚨")
                    print("="*80)
                    print(f"Provider: {provider}")
                    print(f"Model: {model}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    print("Possible reasons:")
                    print("  - Invalid API key")
                    print("  - Quota exceeded")
                    print("  - Insufficient permissions")
                    print("  - Model access not enabled")
                    print("="*80 + "\n")
                
                if response.status_code == 401:
                    print("\n" + "="*80)
                    print("🚨 LLM API AUTHENTICATION FAILED 🚨")
                    print("="*80)
                    print(f"Provider: {provider}")
                    print(f"Model: {model}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    print("Possible reasons:")
                    print("  - Invalid API key")
                    print("  - Expired API key")
                    print("="*80 + "\n")
                
                if response.status_code >= 400:
                    print("\n" + "="*80)
                    print(f"🚨 LLM API ERROR: {response.status_code} 🚨")
                    print("="*80)
                    print(f"Provider: {provider}")
                    print(f"Model: {model}")
                    print(f"URL: {api_url}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    print("="*80 + "\n")
                
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                print(f"\n{'='*80}")
                print(f"✅ LLM API SUCCESS!")
                print(f"{'='*80}")
                print(f"Provider: {provider}")
                print(f"Model: {model}")
                print(f"Response Length: {len(content)} characters")
                print(f"{'='*80}\n")
                
                return content
        
        except httpx.HTTPError as e:
            print("\n" + "="*80)
            print("🚨 LLM API HTTP ERROR 🚨")
            print("="*80)
            print(f"Provider: {provider}")
            print(f"Model: {model}")
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
                detail=f"LLM API error ({provider}): {str(e)}"
            ) from e
        except Exception as e:
            print("\n" + "="*80)
            print("🚨 UNEXPECTED LLM ERROR 🚨")
            print("="*80)
            print(f"Provider: {provider}")
            print(f"Model: {model}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error in LLM generation ({provider}): {str(e)}"
            )
    
    def _get_language_for_region(self, region: str) -> str:
        """Map region to language code"""
        language_map = {
            "US": "en-US",
            "UK": "en-GB",
            "EU": "en-EU",
            "APAC": "en-APAC",
            "LATAM": "es-MX",
            "FR": "fr-FR",
            "DE": "de-DE",
            "ES": "es-ES",
            "JP": "ja-JP",
            "CN": "zh-CN",
            "KR": "ko-KR",
            "IT": "it-IT",
            "BR": "pt-BR",
            "MX": "es-MX",
            "CA": "en-US",
            "AU": "en-GB",
            "India": "en-US",
            "Japan": "ja-JP",
            "China": "zh-CN",
            "Korea": "ko-KR",
            "France": "fr-FR",
            "Germany": "de-DE",
            "Spain": "es-ES",
            "Italy": "it-IT",
            "Brazil": "pt-BR",
            "Mexico": "es-MX"
        }
        return language_map.get(region, "en-US")


# Singleton instance
llm_service = LLMService()
