import httpx
import sys
import os

from Triada.providers.base import LLMProvider

class OpenRouterAdapter(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Override model if provided in kwargs
        model = kwargs.pop("model", self.model)

        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
