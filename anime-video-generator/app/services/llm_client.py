from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.utils.config import Settings


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMResult:
    raw_text: str
    data: Any


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _pick_provider(self) -> str:
        if self.settings.gemini_api_key:
            return "gemini"
        if self.settings.openai_api_key:
            return "openai"
        if self.settings.ollama_host:
            return "ollama"
        return "none"

    @retry(wait=wait_exponential(multiplier=1, min=1, max=12), stop=stop_after_attempt(3))
    async def generate_json(self, *, prompt: str) -> LLMResult:
        provider = self._pick_provider()
        if provider == "none":
            raise LLMError("No LLM provider configured. Set GEMINI_API_KEY, OPENAI_API_KEY or OLLAMA_HOST in .env")

        if provider == "gemini":
            return await self._generate_gemini_json(prompt)
        if provider == "openai":
            return await self._generate_openai_json(prompt)
        return await self._generate_ollama_json(prompt)

    async def _generate_gemini_json(self, prompt: str) -> LLMResult:
        import google.generativeai as genai
        
        genai.configure(api_key=self.settings.gemini_api_key)
        # Choose a stable Gemini model, use gemini-pro or gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # We need JSON so we explicitly tell it.
        instruction = "Return ONLY valid JSON. No markdown formatting, no code blocks."
        
        # Async generation isn't natively perfect in older versions but generate_content_async works in 1.x
        try:
            resp = await model.generate_content_async([instruction, prompt])
            raw_text = resp.text
            # Sometimes Gemini returns markdown code blocks ```json ... ```
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            data = json.loads(clean_text)
            return LLMResult(raw_text=raw_text, data=data)
        except Exception as e:
            raise LLMError(f"Failed to generate/parse Gemini JSON. Error={e}")

    async def _generate_openai_json(self, prompt: str) -> LLMResult:
        # OpenAI Responses API (works with openai>=1.x)
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        resp = await client.responses.create(
            model=self.settings.openai_model,
            input=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        raw_text = str(resp.output_text)
        try:
            data = json.loads(raw_text)
        except Exception as e:
            raise LLMError(f"Failed to parse OpenAI JSON. Error={e}. Raw={raw_text[:500]}")
        return LLMResult(raw_text=raw_text, data=data)

    async def _generate_ollama_json(self, prompt: str) -> LLMResult:
        # Ollama chat API: /api/chat
        url = self.settings.ollama_host.rstrip("/") + "/api/chat"
        payload = {
            "model": self.settings.ollama_model,
            "messages": [
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.7},
        }
        async with httpx.AsyncClient(timeout=180) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            out = r.json()
        raw_text = out["message"]["content"]
        try:
            data = json.loads(raw_text)
        except Exception as e:
            raise LLMError(f"Failed to parse Ollama JSON. Error={e}. Raw={raw_text[:500]}")
        return LLMResult(raw_text=raw_text, data=data)

