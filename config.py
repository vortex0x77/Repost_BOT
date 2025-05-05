import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8037468732:AAFCEbY9NBt0exuF7NSbZqn9-amf4h2Sn8I")
# Преобразует строку с id админов из переменной окружения в список целых чисел
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_ID", "1968139479,5952409238").replace(" ", "").split(",") if x]
DB_PATH = os.getenv("USER_DB_PATH", "school_bot.db")
CLASS_DB_PATH = os.getenv("CLASS_DB_PATH", "classes.db")

# Словарь с эмодзи для различных статусов и действий в боте
EMOJI = {
    'welcome': '🎉', 'question': '❓', 'open': '📚', 'help': '❔',
    'rating': '📊', 'cancel': '❌', 'success': '✅', 'warning': '⚠️', 'error': '🚫',
    'add': '➕', 'check': '📋', 'pin': '📌', 'description': '📝',
    'author': '👤', 'time': '⏳', 'status': '🔮', 'open_status': '✅', 'closed_status': '❌',
    'online': '💻', 'offline': '🏫', 'mail': '✉️', 'target': '🎯', 'trophy': '🏆', 'empty': '📥',
    'calendar': '📅', 'info': 'ℹ️', 'sos': '🆘', 'open_questions': '📚'
}
