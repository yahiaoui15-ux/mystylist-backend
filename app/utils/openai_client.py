"""
OpenAI Client Enhanced v1.1
Wrapper autour du client existant qui AJOUTE le token counting
✅ Backward compatible - peut remplacer openai_client.py directement
✅ Logs détaillés des tokens utilisés
✅ Alermes si approaching limite
"""

import json
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import OPENAI_API_KEY

# Import du token counter
try:
    from app.utils.token_counter import token_counter
    HAS_TOKEN_COUNTER = True
except ImportError:
    HAS_TOKEN_COUNTER = False
    print("⚠️ Token counter not available - logs will be limited")


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.token_counter = token_counter if HAS_TOKEN_COUNTER else None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def analyze_image(self, image_urls: list, prompt: str, model: str = "gpt-4-turbo", max_tokens: int = 4000):
        """
        ✅ NOUVELLE VERSION: Appel OpenAI Vision avec token counting
        
        Args:
            image_urls: URLs des images à analyser
            prompt: Prompt utilisateur
            model: Modèle OpenAI
            max_tokens: Max tokens en sortie (default 4000)
        
        Returns:
            Réponse texte d'OpenAI
        """
        try:
            # ✅ NOUVEAU: Log token budget PRÉ-appel
            if self.token_counter:
                system_prompt = getattr(self, '_current_system_prompt', "")
                self.token_counter.log_colorimetry_call(
                    system_prompt=system_prompt,
                    user_prompt=prompt,
                    image_urls=image_urls,
                    max_output_tokens=max_tokens
                )
            
            # Construire le contenu avec images
            content = [{"type": "text", "text": prompt}]
            for url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": url}
                })
            
            # Appel OpenAI
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
            
            # ✅ NOUVEAU: Log tokens RÉELS après réponse
            if self.token_counter and hasattr(response, 'usage'):
                self.token_counter.log_completion_tokens(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Erreur OpenAI Vision: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def call_chat(self, prompt: str, model: str = "gpt-4-turbo", max_tokens: int = 3000):
        """
        ✅ NOUVELLE VERSION: Appel OpenAI Chat avec token counting
        
        Args:
            prompt: Prompt utilisateur
            model: Modèle OpenAI
            max_tokens: Max tokens en sortie
        
        Returns:
            Réponse texte d'OpenAI
        """
        try:
            # ✅ NOUVEAU: Log token budget PRÉ-appel
            if self.token_counter:
                tokens_before = self.token_counter.count_tokens(prompt)
                print(f"\n🔤 Chat Prompt: {tokens_before} tokens")
            
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
            
            # ✅ NOUVEAU: Log tokens RÉELS
            if self.token_counter and hasattr(response, 'usage'):
                print(f"📊 Chat Response: {response.usage.completion_tokens} tokens utilisés")
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Erreur OpenAI Chat: {e}")
            raise
    
    async def parse_json_response(self, response_text: str) -> dict:
        """
        Parser la réponse JSON d'OpenAI
        (Identique à version précédente)
        """
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
    
    def set_system_prompt(self, system_prompt: str):
        """
        ✅ NOUVELLE MÉTHODE: Stocker le system prompt pour token counting
        
        Args:
            system_prompt: Le system prompt utilisé
        """
        self._current_system_prompt = system_prompt


# Instance globale
openai_client = OpenAIClient()