import sys
sys.dont_write_bytecode = True

# Aiogram imports
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Project imports
from app.config import BOT_TOKEN
from app.handlers import main_router
from app.services import init_classes_db

# Other imports
import asyncio


async def main():
    # Передаём parse_mode через DefaultBotProperties, чтобы все сообщения по умолчанию поддерживали HTML-разметку
    bot = Bot(token='8037468732:AAFCEbY9NBt0exuF7NSbZqn9-amf4h2Sn8I', default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(main_router)
    await init_classes_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main()) 