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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_image(
        self,
        image_urls: list,
        prompt: str,
        model: str = "gpt-4-turbo",
        max_tokens: int = 4000,
    ):
        try:
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
            print(f"❌ Erreur OpenAI Vision: {e}")
            if HAS_CALL_TRACKER:
                call_tracker.log_error(
                    section=self._current_section or "OpenAI",
                    error_msg=f"Vision call failed: {str(e)}",
                )
            raise


# ✅ IMPORTANT: export attendu par le reste du codebase
openai_client = OpenAIClient()

__all__ = ["OpenAIClient", "openai_client"]
