import sys
sys.dont_write_bytecode = True  # Отключает создание .pyc файлов и папки __pycache__

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import router
from services import init_classes_db

async def main():
    # Передаём parse_mode через DefaultBotProperties, чтобы все сообщения по умолчанию поддерживали HTML-разметку
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await init_classes_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())