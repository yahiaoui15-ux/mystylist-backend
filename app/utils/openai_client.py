import os
from typing import Optional, List, Dict, Any

from openai import AsyncOpenAI


class OpenAIClient:
    def __init__(self):
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")

        self.client = AsyncOpenAI(api_key=api_key)

        # Modèles par défaut (tu peux override via env si tu veux)
        self.default_chat_model = (os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini").strip()
        self.default_vision_model = (os.getenv("OPENAI_VISION_MODEL") or "gpt-4o-mini").strip()

    async def call_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.7,
    ) -> str:
        """
        Appel texte (pas d'image). Retourne le content string.
        """
        used_model = (model or self.default_chat_model).strip()

        resp = await self.client.chat.completions.create(
            model=used_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return (resp.choices[0].message.content or "").strip()

    async def analyze_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_url: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> str:
        """
        Appel vision via chat.completions avec content multi-part (text + image_url).
        IMPORTANT: nécessite un modèle compatible image_url (ex: gpt-4o / gpt-4o-mini).
        """
        used_model = (model or self.default_vision_model).strip()

        resp = await self.client.chat.completions.create(
            model=used_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return (resp.choices[0].message.content or "").strip()


openai_client = OpenAIClient()
