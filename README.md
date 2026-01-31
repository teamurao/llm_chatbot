# LLM Bot Lesson Project

Учебный проект под занятие «Подключение LLM (OpenAI / DeepSeek / Hugging Face)».
Цель — показать архитектуру: `handler → llm_client → LLM API`, безопасность ключей,
таймауты и лимиты, а также возможность смены провайдера без переписывания бота.

## Что внутри

- `bot/services/llm_client.py` — единый клиент LLM с выбором провайдера
- `bot/handlers/ask_handler.py` — команда `/ask` в aiogram
- `bot/config.py` — загрузка настроек и ключей из окружения
- `docs/sequence.mmd` — диаграмма последовательности занятия

## Быстрый старт

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Создайте файл `.env` по примеру `env.example` и вставьте ключи.
3. Запустите бота:
   ```bash
   python -m bot.main
   ```

## Архитектура

Мини-схема:

User → Telegram Bot → LLM API → Bot → User

Хендлеры не делают запросы напрямую — они вызывают `LLMClient`.
Это упрощает замену провайдера и тестирование.

## Смена провайдера

В `.env` установите `LLM_PROVIDER`:

- `openai` — OpenAI через SDK
- `deepseek` — OpenAI-совместимый API DeepSeek
- `huggingface` — Hugging Face Inference API

## Важные тезисы

- LLM — "внешний платный API", а не «магическая функция»
- API-ключ = деньги, хранить только в `.env`
- Таймауты и лимиты — нормальная часть работы с LLM
