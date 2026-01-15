"""
OpenAI Client v2.0 - Amélioré avec call_tracker
✅ Retourne content + usage tokens
✅ Compatible avec call_tracker pour logs structurés
✅ Backward compatible (peut retourner juste content si besoin)
"""

import json
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import OPENAI_API_KEY

# Import du call tracker
try:
    from app.utils.openai_call_tracker import call_tracker
    HAS_CALL_TRACKER = True
except ImportError:
    HAS_CALL_TRACKER = False
    print("⚠️ Call tracker not available - some logs will be limited")


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self._current_system_prompt = ""
        self._current_section = ""  # "Colorimetry", "Morphology", "Styling"
        self._current_subsection = ""  # "Part 1", "Part 2", etc.
    
    def set_context(self, section: str, subsection: str = ""):
        """
        Définir le contexte pour le tracking
        
        Args:
            section: "Colorimetry", "Morphology", "Styling"
            subsection: "Part 1", "Part 2", "Part 3", ou ""
        """
        self._current_section = section
        self._current_subsection = subsection
    
    def set_system_prompt(self, system_prompt: str):
        """Stocker le system prompt"""
        self._current_system_prompt = system_prompt
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def analyze_image(
        self,
        image_urls: list,
        prompt: str,
        model: str = "gpt-4-turbo",
        max_tokens: int = 4000
    ):
        """
        ✅ Appel OpenAI Vision avec token tracking
        
        Args:
            image_urls: URLs des images à analyser
            prompt: Prompt utilisateur
            model: Modèle OpenAI
            max_tokens: Max tokens en sortie
        
        Returns:
            {
                "content": "réponse texte",
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int
            }
        """
        try:
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
            
            # Extraire le contenu et les tokens
            content_text = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
            completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
            total_tokens = prompt_tokens + completion_tokens
            
            # Log via call_tracker si disponible
            if HAS_CALL_TRACKER and self._current_section:
                call_tracker.log_api_call(
                    section=self._current_section,
                    subsection=self._current_subsection,
                    service="openai_client",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    raw_response_preview=content_text,
                    parse_success=True
                )
            
            # Retourner les tokens aussi
            return {
                "content": content_text,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
            
        except Exception as e:
            print(f"❌ Erreur OpenAI Vision: {e}")
            if HAS_CALL_TRACKER:
                call_tracker.log_error(
                    section=self._current_section or "OpenAI",
                    error_msg=f"Vision call failed: {str(e)}"
                )
            raise
    
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_chat(
    self,
    prompt: str,
    model: str = "gpt-4",
    max_tokens: int = 3000,
    temperature: float = 0.2,
    response_format: dict = None
):
    """
    ✅ Appel OpenAI Chat avec token tracking + finish_reason + system prompt + response_format optionnel
    """
    try:
        messages = []

        # ✅ IMPORTANT: injecter réellement le system prompt si présent
        if self._current_system_prompt:
            messages.append({"role": "system", "content": self._current_system_prompt})

        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        # ✅ Optionnel: forcer JSON valide si le modèle supporte
        if response_format:
            kwargs["response_format"] = response_format

        response = await self.client.chat.completions.create(**kwargs)

        content_text = response.choices[0].message.content
        finish_reason = getattr(response.choices[0], "finish_reason", None)

        prompt_tokens = response.usage.prompt_tokens if hasattr(response, "usage") else 0
        completion_tokens = response.usage.completion_tokens if hasattr(response, "usage") else 0
        total_tokens = prompt_tokens + completion_tokens

        if HAS_CALL_TRACKER and self._current_section:
            call_tracker.log_api_call(
                section=self._current_section,
                subsection=self._current_subsection,
                service="openai_client",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                raw_response_preview=content_text,
                parse_success=True
            )

        return {
            "content": content_text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "finish_reason": finish_reason,  # ✅ AJOUT
        }

    except Exception as e:
        print(f"❌ Erreur OpenAI Chat: {e}")
        if HAS_CALL_TRACKER:
            call_tracker.log_error(
                section=self._current_section or "OpenAI",
                error_msg=f"Chat call failed: {str(e)}"
            )
        raise
    
    async def parse_json_response(self, response_text: str) -> dict:
        """Parser la réponse JSON d'OpenAI"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            try:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            print(f"❌ Erreur parsing JSON: {response_text[:100]}")
            return {}


# Instance globale
openai_client = OpenAIClient()