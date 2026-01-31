import asyncio
import logging
import os
import sys

project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.config import load_settings
from bot.handlers import ask_handler
from bot.services.llm_client import LLMClient


async def main() -> None:
    load_dotenv()
    settings = load_settings()

    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.telegram_token)
    dp = Dispatcher()

    llm_client = LLMClient(settings)
    dp.include_router(ask_handler.register(llm_client))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
