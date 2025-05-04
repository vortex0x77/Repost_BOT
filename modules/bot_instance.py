import os
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
token = os.getenv("BOT_TOKEN")
if not token:
    token = "8037468732:AAFCEbY9NBt0exuF7NSbZqn9-amf4h2Sn8I"  # Fallback to hardcoded token

# Create bot instance with HTML parsing
bot = telebot.TeleBot(token, parse_mode="HTML")