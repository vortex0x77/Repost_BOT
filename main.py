import sys
sys.dont_write_bytecode = True  # Отключение создания .pyc файлов

import os
from dotenv import load_dotenv

from modules.bot_instance import bot
from modules.database import init_databases
from modules.handlers import register_all_handlers

# Загрузка переменных окружения из .env файла
load_dotenv()

def main():
    # Инициализация баз данных
    init_databases()
    
    # Регистрация всех обработчиков сообщений
    register_all_handlers()
    
    print("Bot started successfully!")
    # Запуск бесконечного опроса сервера Telegram
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    main()