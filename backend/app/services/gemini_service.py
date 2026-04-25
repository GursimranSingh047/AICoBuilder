"""
gemini_service.py — ProjectPilot AI Layer (FINAL FIXED VERSION)
"""

import json
import re
from typing import Any, Optional

import httpx
from loguru import logger

from app.core.config import settings


# ── Constants ──────────────────────────────────────────────────────────────────

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

_MODEL_FALLBACK_CHAIN = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-1.0-pro",
]


class GeminiService:
    def __init__(self):
        # API key and model
        self._api_key: Optional[str] = settings.GEMINI_API_KEY
        self._model: str = settings.GEMINI_MODEL or _MODEL_FALLBACK_CHAIN[0]

        self._client = httpx.Client(timeout=60.0)

        # Detect OpenAI key format vs OpenRouter vs Gemini
        # OpenAI keys: sk-proj-... or sk-... (but not sk-or-...)
        # OpenRouter keys: sk-or-v1-...
        # Gemini keys: AIza...
        self._use_openai = bool(
            self._api_key 
            and str(self._api_key).startswith("sk-") 
            and not str(self._api_key).startswith("sk-or-")
        )
        self._use_openrouter = bool(
            self._api_key 
            and str(self._api_key).startswith("sk-or-")
        )

        if not self._api_key:
            logger.warning("openai_api_key is not set.")
        else:
            if self._use_openrouter:
                provider = "OpenRouter"
            elif self._use_openai:
                provider = "OpenAI"
            else:
                provider = "Gemini"
            logger.info(f"GeminiService ready | provider={provider} model={self._model}")

    # ── Internal HTTP helper ──────────────────────────────────────────────────

    def _post(self, model: str, payload: dict) -> str:
        # Safety check
        if not self._api_key:
            raise RuntimeError("Missing API key (openai_api_key)")

        if self._use_openrouter:
            # Call OpenRouter API (OpenAI-compatible)
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",  # Optional but recommended
                "X-Title": "ProjectPilot"  # Optional but recommended
            }

            resp = self._client.post(url, json=payload, headers=headers)

            if resp.status_code != 200:
                try:
                    detail = resp.json().get("error", {}).get("message", resp.text)
                except Exception:
                    detail = resp.text

                raise RuntimeError(f"OpenRouter API error {resp.status_code} (model={model}): {detail}")

            data = resp.json()
            try:
                choice = data.get("choices", [])[0]
                if "message" in choice:
                    return choice["message"].get("content", "")
                return choice.get("text", "")
            except Exception:
                raise RuntimeError(f"Unexpected OpenRouter response: {data}")

        elif self._use_openai:
            # Call OpenAI Chat Completions API
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

            resp = self._client.post(url, json=payload, headers=headers)

            if resp.status_code != 200:
                try:
                    detail = resp.json().get("error", {}).get("message", resp.text)
                except Exception:
                    detail = resp.text

                raise RuntimeError(f"OpenAI API error {resp.status_code} (model={model}): {detail}")

            data = resp.json()
            # Support both choices[0].message.content and choices[0].text
            try:
                choice = data.get("choices", [])[0]
                if "message" in choice:
                    return choice["message"].get("content", "")
                return choice.get("text", "")
            except Exception:
                raise RuntimeError(f"Unexpected OpenAI response: {data}")

        # Fallback to Gemini
        url = f"{_BASE_URL}/models/{model}:generateContent?key={self._api_key}"
        resp = self._client.post(url, json=payload)

        if resp.status_code != 200:
            try:
                detail = resp.json().get("error", {}).get("message", resp.text)
            except Exception:
                detail = resp.text

            raise RuntimeError(
                f"Gemini API error {resp.status_code} (model={model}): {detail}"
            )

        data = resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected Gemini response: {data}")

    def _call(self, prompt: str) -> str:
        if not self._api_key:
            return self._mock(prompt)

        models_to_try = [self._model] + [
            m for m in _MODEL_FALLBACK_CHAIN if m != self._model
        ]

        last_error = None

        for model in models_to_try:
            try:
                # Build payload depending on provider
                if self._use_openrouter or self._use_openai:
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2048,
                    }
                else:
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.7,
                            "topP": 0.9,
                            "maxOutputTokens": 2048,
                        },
                    }
                
                return self._post(model, payload)
            except RuntimeError as e:
                logger.warning(f"Model {model} failed: {e}")
                last_error = e

        logger.error(f"All models failed: {last_error}")
        return self._mock(prompt)

    # ── Debug helper ──────────────────────────────────────────────────────────

    def list_available_models(self) -> list:
        if not self._api_key:
            return ["API key not configured"]

        try:
            if self._use_openai:
                # OpenAI doesn't provide a simple list via public endpoint without auth; return model hint
                return [self._model]
            resp = self._client.get(f"{_BASE_URL}/models?key={self._api_key}")
            resp.raise_for_status()

            models = resp.json().get("models", [])

            return [
                m["name"].replace("models/", "")
                for m in models
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]

        except Exception as e:
            return [f"Error: {str(e)}"]

    # ── Mock ──────────────────────────────────────────────────────────────────

    def _mock(self, prompt: str) -> str:
        return f"[MOCK] Gemini not configured. Prompt: {prompt[:50]}"

    def _extract_json(self, text: str) -> dict:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass

        try:
            return json.loads(text)
        except:
            return {"raw": text}

    # ── Public API ────────────────────────────────────────────────────────────

    def generate_project_code(self, idea: str, stack: dict) -> dict:
        prompt = f"""
Generate project code.

Idea: {idea}
Stack: {json.dumps(stack)}

Return JSON only.
"""
        return self._extract_json(self._call(prompt))

    def generate_readme(self, idea: str, stack: dict, project_name: str) -> str:
        prompt = f"""
Write README for {project_name}.
"""
        return self._call(prompt)

    def chat(self, message: str, history: list, context: str = "") -> str:
        # ✅ FIX 4: history safety
        history = history or []

        history_text = "\n".join(
            f"{h['role'].upper()}: {h['content']}" for h in history[-10:]
        )

        prompt = f"""
You are an AI assistant.

{context}

{history_text}

User: {message}
"""
        return self._call(prompt)

    def improve_code(self, code: str, instruction: str) -> str:
        prompt = f"""
Improve code:
{code}

Instruction:
{instruction}
"""
        return self._call(prompt)

    def explain_code(self, code: str) -> str:
        prompt = f"""
Explain code:
{code}
"""
        return self._call(prompt)


# Singleton
gemini_service = GeminiService()