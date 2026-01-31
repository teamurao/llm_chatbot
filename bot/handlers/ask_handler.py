from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.llm_client import LLMClient

router = Router()


def register(llm_client: LLMClient) -> Router:
    router.message(Command("ask"))(ask_handler(llm_client))
    return router


def ask_handler(llm_client: LLMClient):
    async def _handler(message: Message) -> None:
        text = message.text.replace("/ask", "").strip() if message.text else ""
        if not text:
            await message.answer("Задайте вопрос после команды /ask")
            return

        await message.answer("Думаю...")
        answer = await llm_client.ask(text)
        await message.answer(answer)

    return _handler
