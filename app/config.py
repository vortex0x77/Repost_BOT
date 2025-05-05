import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS').replace(' ', '').split(',') if x]
DB_PATH = os.getenv("USER_DB_PATH")
CLASS_DB_PATH = os.getenv("CLASS_DB_PATH")


class Settings:
    compact_string_length: int = 50
    max_title_length: int      = 100
    helper_bot_url: str        = "https://t.me/AcadeMix_Support_bot"

