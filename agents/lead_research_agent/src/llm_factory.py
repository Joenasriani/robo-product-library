import os
import json
import asyncio
from abc import ABC, abstractmethod
import httpx

TIMEOUT = httpx.Timeout(60.0, connect=10.0)

async def _post_with_retry(client, url, headers, data, timeout=TIMEOUT):
    last_exc = None
    for attempt in range(3):
        try:
            response = await client.post(url, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()
            return response
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            last_exc = exc
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
    raise last_exc

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, model, base_url="https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        async with httpx.AsyncClient() as client:
            response = await _post_with_retry(client, f"{self.base_url}/chat/completions", headers, data)
        return response.json()["choices"][0]["message"]["content"]

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
        data = {"model": self.model, "max_tokens": 2048, "system": "Return one valid JSON object only.", "messages": [{"role": "user", "content": prompt}]}
        async with httpx.AsyncClient() as client:
            response = await _post_with_retry(client, "https://api.anthropic.com/v1/messages", headers, data)
        result = response.json()
        return result["content"][0]["text"] if result.get("content") else json.dumps(result)

class GeminiProvider(LLMProvider):
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json", "temperature": 0.2}}
        async with httpx.AsyncClient() as client:
            response = await _post_with_retry(client, url, headers, data)
        result = response.json()
        if result.get("candidates"):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        return json.dumps(result)

class LocalProvider(LLMProvider):
    def __init__(self, model="local-model"):
        self.model = model
        self.base_url = "http://localhost:11434/v1"

    async def _detect_endpoint(self):
        async with httpx.AsyncClient() as client:
            for url, check in [("http://localhost:11434/v1", "http://localhost:11434/api/tags"), ("http://localhost:1234/v1", "http://localhost:1234/v1/models")]:
                try:
                    r = await client.get(check, timeout=2.0)
                    if r.status_code == 200:
                        return url
                except Exception:
                    pass
        return "http://localhost:11434/v1"

    async def generate(self, prompt: str) -> str:
        self.base_url = await self._detect_endpoint()
        headers = {"Content-Type": "application/json"}
        data = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False}
        async with httpx.AsyncClient() as client:
            response = await _post_with_retry(client, f"{self.base_url}/chat/completions", headers, data, timeout=httpx.Timeout(120.0, connect=10.0))
        return response.json()["choices"][0]["message"]["content"]

def get_llm_provider():
    provider_type = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    if provider_type == "openai":
        return OpenAIProvider(os.getenv("OPENAI_API_KEY"), model, os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    if provider_type == "anthropic":
        return AnthropicProvider(os.getenv("ANTHROPIC_API_KEY"), model)
    if provider_type == "gemini":
        return GeminiProvider(os.getenv("GEMINI_API_KEY"), model)
    if provider_type == "local":
        return LocalProvider(model)
    raise ValueError("Unknown provider")

async def get_available_providers():
    providers = []
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    if os.getenv("GEMINI_API_KEY"):
        providers.append("gemini")
    async with httpx.AsyncClient() as client:
        for check_url in ["http://localhost:11434/api/tags", "http://localhost:1234/v1/models"]:
            try:
                r = await client.get(check_url, timeout=1.0)
                if r.status_code == 200:
                    providers.append("local")
                    break
            except Exception:
                pass
    return providers
