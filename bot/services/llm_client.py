from bot.config import Settings
from bot.services.providers import (
    HuggingFaceConfig,
    HuggingFaceProvider,
    LLMProviderError,
    OpenAIConfig,
    OpenAIProvider,
)


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider = self._build_provider()

    def _build_provider(self):
        provider = self._settings.llm_provider
        if provider == "openai":
            return OpenAIProvider(
                OpenAIConfig(
                    api_key=self._settings.openai_api_key,
                    model=self._settings.openai_model,
                    timeout_sec=self._settings.timeout_sec,
                    max_tokens=self._settings.max_tokens,
                )
            )
        if provider == "deepseek":
            return OpenAIProvider(
                OpenAIConfig(
                    api_key=self._settings.deepseek_api_key,
                    model=self._settings.deepseek_model,
                    timeout_sec=self._settings.timeout_sec,
                    max_tokens=self._settings.max_tokens,
                ),
                base_url="https://api.deepseek.com",
            )
        if provider == "huggingface":
            return HuggingFaceProvider(
                HuggingFaceConfig(
                    api_key=self._settings.hf_api_key,
                    model=self._settings.hf_model,
                    base_url=self._settings.hf_base_url,
                    timeout_sec=self._settings.timeout_sec,
                    max_tokens=self._settings.max_tokens,
                )
            )
        raise ValueError(f"Unknown provider: {provider}")

    async def ask(self, prompt: str) -> str:
        if len(prompt) > self._settings.max_prompt_chars:
            return "Вопрос слишком длинный"

        try:
            return await self._provider.ask(prompt)
        except LLMProviderError as exc:
            if str(exc) == "timeout":
                return "Модель не ответила вовремя"
            return "Ошибка при обращении к модели"
