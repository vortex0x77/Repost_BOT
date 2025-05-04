import os
import telebot
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("BOT_TOKEN")
if not token:
    token = "7897665316:AAGQZ6huwcfV2_C9B3AlrB7BD9r7A33uNxU"

bot = telebot.TeleBot(token, parse_mode="HTML")
