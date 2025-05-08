import os
from dotenv import load_dotenv

load_dotenv()
ADMINS = 5952409238
BOT_TOKEN = os.getenv('BOT_TOKEN')
admin_ids_str = os.getenv('ADMIN_IDS')
ADMIN_IDS = [int(x) for x in admin_ids_str.split(',') if x] if admin_ids_str else []
if ADMINS not in ADMIN_IDS:
    ADMIN_IDS.append(ADMINS)
DB_PATH = os.getenv("USER_DB_PATH")
CLASS_DB_PATH = os.getenv("CLASS_DB_PATH")

class Settings:
    compact_string_length: int = 50
    max_title_length: int      = 100
    helper_bot_url: str        = "https://t.me/AcadeMix_Support_bot"
