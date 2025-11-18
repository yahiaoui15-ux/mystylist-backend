import json
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import OPENAI_API_KEY

class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def analyze_image(self, image_urls: list, prompt: str, model: str = "gpt-4o", max_tokens: int = 4000):
        """Appel OpenAI Vision avec retry automatique"""
        try:
            # Construire le contenu avec images
            content = [{"type": "text", "text": prompt}]
            for url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": url}
                })
            
            response = await self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Erreur OpenAI Vision: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def call_chat(self, prompt: str, model: str = "gpt-4o", max_tokens: int = 3000):
        """Appel OpenAI Chat (pas vision) avec retry"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Erreur OpenAI Chat: {e}")
            raise
    
    async def parse_json_response(self, response_text: str) -> dict:
        """Parser la réponse JSON d'OpenAI"""
        try:
            # Essayer de parser directement
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Si erreur, chercher le JSON dans la réponse
            try:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            print(f"❌ Erreur parsing JSON: {response_text}")
            return {}

# Instance globale
openai_client = OpenAIClient()