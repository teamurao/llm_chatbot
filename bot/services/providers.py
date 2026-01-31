import asyncio
from dataclasses import dataclass

import httpx
from openai import AsyncOpenAI


class LLMProviderError(Exception):
    pass


class BaseProvider:
    async def ask(self, prompt: str) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str
    timeout_sec: int
    max_tokens: int


class OpenAIProvider(BaseProvider):
    def __init__(self, config: OpenAIConfig, base_url: str | None = None) -> None:
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            timeout=float(config.timeout_sec),
            base_url=base_url,
        )
        self._model = config.model
        self._max_tokens = config.max_tokens

    async def ask(self, prompt: str) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Ты полезный ассистент"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self._max_tokens,
            )
            return response.choices[0].message.content or ""
        except asyncio.TimeoutError as exc:
            raise LLMProviderError("timeout") from exc
        except Exception as exc:
            raise LLMProviderError("provider_error") from exc


@dataclass(frozen=True)
class HuggingFaceConfig:
    api_key: str
    model: str
    base_url: str
    timeout_sec: int
    max_tokens: int


class HuggingFaceProvider(BaseProvider):
    def __init__(self, config: HuggingFaceConfig) -> None:
        self._model = config.model
        self._base_url = config.base_url
        self._timeout = config.timeout_sec
        self._max_tokens = config.max_tokens
        self._headers = {"Authorization": f"Bearer {config.api_key}"}

    def _format_prompt(self, prompt: str) -> str:
        if "saiga_llama3_8b" in self._model.lower():
            return (
                "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
                "Ты полезный ассистент.\n"
                "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
                f"{prompt}\n"
                "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
            )
        return prompt

    async def _ask_router(self, prompt: str) -> str:
        url = self._base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": "Ты полезный ассистент."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self._max_tokens,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=self._headers)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise LLMProviderError("timeout") from exc
        except Exception as exc:
            raise LLMProviderError("provider_error") from exc

        if isinstance(data, dict):
            choices = data.get("choices") or []
            if choices and isinstance(choices, list):
                message = choices[0].get("message", {})
                content = message.get("content")
                if isinstance(content, str):
                    return content
            if "error" in data:
                raise LLMProviderError("provider_error")
        return ""

    async def ask(self, prompt: str) -> str:
        if self._base_url:
            if "router.huggingface.co" in self._base_url:
                return await self._ask_router(prompt)
            url = self._base_url.rstrip("/")
        else:
            url = f"https://api-inference.huggingface.co/models/{self._model}"
        payload = {
            "inputs": self._format_prompt(prompt),
            "parameters": {
                "max_new_tokens": self._max_tokens,
                "return_full_text": False,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=self._headers)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise LLMProviderError("timeout") from exc
        except Exception as exc:
            raise LLMProviderError("provider_error") from exc

        if isinstance(data, list) and data:
            generated = data[0].get("generated_text")
            if isinstance(generated, str):
                return generated
        if isinstance(data, dict) and "estimated_time" in data:
            return "Модель загружается, попробуйте позже"
        if isinstance(data, dict) and "error" in data:
            raise LLMProviderError("provider_error")
        return ""
