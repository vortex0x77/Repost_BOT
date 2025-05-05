import os
import telebot
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена бота из переменных окружения
token = os.getenv("BOT_TOKEN")
if not token:
    token = "8037468732:AAFCEbY9NBt0exuF7NSbZqn9-amf4h2Sn8I"

# Создание экземпляра бота с указанным токеном и HTML-форматированием сообщений
bot = telebot.TeleBot(token, parse_mode="HTML")