"""
Scrui LLM Client.
Unified multi-provider client for OpenRouter, Groq, Gemini, and Ollama.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Optional, Dict, Any


class LLMClient:
    """Connects to AI inference providers for code generation."""

    def __init__(
        self,
        provider: str = "openrouter",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.provider = provider.lower()
        self.api_key = api_key or self._detect_api_key(self.provider)
        self.model = model or self._default_model(self.provider)

    def _detect_api_key(self, provider: str) -> Optional[str]:
        if provider == "openrouter":
            return os.environ.get("OPENROUTER_API_KEY")
        elif provider == "groq":
            return os.environ.get("GROQ_API_KEY")
        elif provider == "gemini":
            return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        return None

    def _default_model(self, provider: str) -> str:
        defaults = {
            "openrouter": "anthropic/claude-3.7-sonnet",
            "groq": "llama-3.3-70b-versatile",
            "gemini": "gemini-2.0-flash",
            "ollama": "qwen2.5-coder:14b",
        }
        return defaults.get(provider, "gpt-4o")

    def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Synchronously request completion from the configured provider."""
        if not self.api_key and self.provider != "ollama":
            # Return empty to allow scaffolder to fall back to template-based generation
            return ""

        if self.provider == "openrouter":
            return self._call_openrouter(system_prompt, user_prompt)
        elif self.provider == "groq":
            return self._call_groq(system_prompt, user_prompt)
        elif self.provider == "ollama":
            return self._call_ollama(system_prompt, user_prompt)
        return ""

    def _call_openrouter(self, system: str, user: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/brovk2008/Scrui",
            "X-Title": "Scrui Code Scaffolder",
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                return res_data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Scrui Generator] OpenRouter request failed: {e}")
            return ""

    def _call_groq(self, system: str, user: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                return res_data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Scrui Generator] Groq request failed: {e}")
            return ""

    def _call_ollama(self, system: str, user: str) -> str:
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                return res_data["message"]["content"]
        except Exception as e:
            print(f"[Scrui Generator] Local Ollama request failed: {e}")
            return ""
