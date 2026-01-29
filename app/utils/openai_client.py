import json
import base64
import mimetypes
import httpx
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import OPENAI_API_KEY

try:
    from app.utils.openai_call_tracker import call_tracker
    HAS_CALL_TRACKER = True
except ImportError:
    HAS_CALL_TRACKER = False
    print("⚠️ Call tracker not available - some logs will be limited")


# Modèles "vision-capable" (au sens: acceptent content items type=image_url)
# On force un fallback si un modèle non compatible est demandé (ex: gpt-4-turbo).
VISION_FALLBACK_MODEL = "gpt-4o-mini"


class OpenAIClient:
    def __init__(self):
        if not OPENAI_API_KEY or not str(OPENAI_API_KEY).strip():
            raise RuntimeError("OPENAI_API_KEY is missing or empty")
        self.client = AsyncOpenAI(api_key=str(OPENAI_API_KEY).strip())
        self._current_system_prompt = ""
        self._current_section = ""
        self._current_subsection = ""

    def set_context(self, section: str, subsection: str = ""):
        self._current_section = section
        self._current_subsection = subsection

    def set_system_prompt(self, system_prompt: str):
        self._current_system_prompt = system_prompt

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _is_vision_capable_model(model: str) -> bool:
        """
        Heuristique simple.
        - gpt-4o / gpt-4o-mini / gpt-4.1* acceptent image_url
        - gpt-4-turbo (chat.completions) peut échouer selon config/lib -> on fallback
        """
        if not model:
            return False
        m = model.lower()
        return ("gpt-4o" in m) or ("gpt-4.1" in m)

    @staticmethod
    def _normalize_model_for_vision(model: str) -> str:
        if OpenAIClient._is_vision_capable_model(model):
            return model
        return VISION_FALLBACK_MODEL

    async def _url_to_data_url(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            r = await client.get(url)
            r.raise_for_status()

            content_type = (r.headers.get("content-type") or "").split(";")[0].strip()
            if not content_type:
                guessed, _ = mimetypes.guess_type(url)
                content_type = guessed or "image/jpeg"

            b64 = base64.b64encode(r.content).decode("utf-8")
            return f"data:{content_type};base64,{b64}"

    # ---------------------------------------------------------------------
    # TEXT (Chat) calls
    # ---------------------------------------------------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_chat(
        self,
        prompt: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: str | None = None,
        extra_messages: list | None = None,
    ):
        """
        Appel texte standard.
        Compat avec le codebase: services attendent self.openai.call_chat(...)
        """
        try:
            messages = []

            sys_prompt = system_prompt if system_prompt is not None else self._current_system_prompt
            if sys_prompt:
                messages.append({"role": "system", "content": sys_prompt})

            if extra_messages:
                # extra_messages doit déjà être sous forme [{"role": "...","content": "..."}]
                messages.extend(extra_messages)

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )

            content_text = response.choices[0].message.content
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
                    parse_success=True,
                )

            return {
                "content": content_text,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }

        except Exception as e:
            print(f"❌ Erreur OpenAI Chat: {e}")
            if HAS_CALL_TRACKER:
                call_tracker.log_error(
                    section=self._current_section or "OpenAI",
                    error_msg=f"Chat call failed: {str(e)}",
                )
            raise

    # ---------------------------------------------------------------------
    # VISION calls (images)
    # ---------------------------------------------------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_image(
        self,
        image_urls: list,
        prompt: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.2,
    ):
        """
        Appel vision: construit content items avec image_url.
        IMPORTANT: si un modèle non compatible est fourni (ex gpt-4-turbo), on fallback automatiquement.
        """
        try:
            model = self._normalize_model_for_vision(model)

            # 1) Construire contenu (texte + images en data URL)
            content = [{"type": "text", "text": prompt}]
            for url in image_urls:
                data_url = await self._url_to_data_url(url)
                content.append({"type": "image_url", "image_url": {"url": data_url}})

            # 2) Construire messages (avec system prompt si présent)
            messages = []
            if self._current_system_prompt:
                messages.append({"role": "system", "content": self._current_system_prompt})
            messages.append({"role": "user", "content": content})

            # 3) Appel OpenAI
            response = await self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )

            content_text = response.choices[0].message.content
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
                    parse_success=True,
                )

            return {
                "content": content_text,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "model_used": model,
            }

        except Exception as e:
            print(f"❌ Erreur OpenAI Vision: {e}")
            if HAS_CALL_TRACKER:
                call_tracker.log_error(
                    section=self._current_section or "OpenAI",
                    error_msg=f"Vision call failed: {str(e)}",
                )
            raise


# ✅ export attendu par le reste du codebase
openai_client = OpenAIClient()

__all__ = ["OpenAIClient", "openai_client"]
