import os
from dataclasses import dataclass


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    llm_provider: str
    openai_api_key: str
    openai_model: str
    deepseek_api_key: str
    deepseek_model: str
    hf_api_key: str
    hf_model: str
    hf_base_url: str
    timeout_sec: int
    max_prompt_chars: int
    max_tokens: int


def load_settings() -> Settings:
    return Settings(
        telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        llm_provider=os.getenv("LLM_PROVIDER", "openai").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        hf_api_key=os.getenv("HUGGINGFACE_API_KEY", ""),
        hf_model=os.getenv("HUGGINGFACE_MODEL", "gpt2"),
        hf_base_url=os.getenv("HUGGINGFACE_BASE_URL", "").strip(),
        timeout_sec=_get_int("LLM_TIMEOUT_SEC", 15),
        max_prompt_chars=_get_int("LLM_MAX_PROMPT_CHARS", 1000),
        max_tokens=_get_int("LLM_MAX_TOKENS", 300),
    )
