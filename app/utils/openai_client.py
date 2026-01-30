import os
import time
import re
from typing import Optional, Dict, Any, List

from openai import AsyncOpenAI


class OpenAIClient:
    """
    Client OpenAI "compatible projet" :
    - supporte set_context() + set_system_prompt()
    - call_chat(prompt=...) retourne un dict {content, tokens, finish_reason, model}
    - analyze_image(image_urls=[...], prompt=...) retourne un dict idem
    """

    def __init__(self):
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")

        self.client = AsyncOpenAI(api_key=api_key)

        self.default_chat_model = (os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini").strip()
        self.default_vision_model = (os.getenv("OPENAI_VISION_MODEL") or "gpt-4o-mini").strip()

        self._context_scope: str = ""
        self._context_step: str = ""
        self._system_prompt: str = ""

    def set_context(self, scope: str, step: str = "") -> None:
        self._context_scope = str(scope or "")
        self._context_step = str(step or "")

    def set_system_prompt(self, system_prompt: str) -> None:
        self._system_prompt = str(system_prompt or "")

    def _build_return(
        self,
        content: str,
        model: str,
        usage: Any,
        finish_reason: Optional[str],
        started_at: float,
    ) -> Dict[str, Any]:
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
        total_tokens = (
            int(getattr(usage, "total_tokens", prompt_tokens + completion_tokens) or (prompt_tokens + completion_tokens))
            if usage
            else (prompt_tokens + completion_tokens)
        )

        return {
            "content": (content or "").strip(),
            "model": model,
            "finish_reason": finish_reason,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "duration_seconds": round(time.time() - started_at, 3),
            "context": {"scope": self._context_scope, "step": self._context_step},
        }

    _DATA_URL_RE = re.compile(r"^data:image\/[a-zA-Z0-9.+-]+;base64,", re.IGNORECASE)

    async def call_chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.7,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        used_model = (model or self.default_chat_model).strip()
        started_at = time.time()

        messages = []
        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})
        messages.append({"role": "user", "content": str(prompt or "")})

        kwargs: Dict[str, Any] = {
            "model": used_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        resp = await self.client.chat.completions.create(**kwargs)

        content = (resp.choices[0].message.content or "") if resp and resp.choices else ""
        finish_reason = (resp.choices[0].finish_reason if resp and resp.choices else None)

        return self._build_return(
            content=content,
            model=used_model,
            usage=getattr(resp, "usage", None),
            finish_reason=finish_reason,
            started_at=started_at,
        )

    async def analyze_image(
        self,
        image_urls: List[str],
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.2,
        response_format: Optional[Dict[str, Any]] = None,
        vision_detail_override: Optional[str] = None,  # 👈 AJOUT

    ) -> Dict[str, Any]:
        used_model = (model or self.default_vision_model).strip()
        started_at = time.time()

        vision_detail = (
            vision_detail_override
            or (os.getenv("OPENAI_VISION_DETAIL") or "low")
        ).strip().lower()

        if vision_detail not in ("low", "high", "auto"):
            vision_detail = "low"

        content_parts: List[Dict[str, Any]] = [{"type": "text", "text": str(prompt or "")}]

        print("DEBUG analyze_image:")
        print(" - used_model:", used_model)
        print(" - images_count:", len(image_urls or []))
        print(" - vision_detail:", vision_detail)

        for url in (image_urls or []):
            u = str(url or "").strip()
            if not u:
                continue

            print(" - image_url raw (preview):", u[:120])

            # IMPORTANT: on n'encode PAS en base64 (sinon tokens explosent).
            # Si data URL, on la garde. Sinon on envoie l'URL distante.
            final_url = u
            if self._DATA_URL_RE.match(u):
                print(" - image_url mode: data_url (already)")
            else:
                print(" - image_url mode: remote_url")

            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": final_url, "detail": vision_detail},
                }
            )

        messages = []
        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})
        messages.append({"role": "user", "content": content_parts})

        kwargs: Dict[str, Any] = {
            "model": used_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        resp = await self.client.chat.completions.create(**kwargs)

        content = (resp.choices[0].message.content or "") if resp and resp.choices else ""
        finish_reason = (resp.choices[0].finish_reason if resp and resp.choices else None)

        return self._build_return(
            content=content,
            model=used_model,
            usage=getattr(resp, "usage", None),
            finish_reason=finish_reason,
            started_at=started_at,
        )


openai_client = OpenAIClient()
