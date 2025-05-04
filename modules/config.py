import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database paths
DB_PATH = os.getenv("USER_DB_PATH", "school_bot.db")
CLASS_DB_PATH = os.getenv("CLASS_DB_PATH", "classes.db")

# Admin configuration
ADMIN_IDS = []
admin_ids_str = os.getenv("ADMIN_ID", "1968139479")
try:
    # Handle comma-separated list of admin IDs
    for admin_id in admin_ids_str.replace(" ", "").split(","):
        if admin_id:
            ADMIN_IDS.append(int(admin_id))
    
    # Ensure we have at least one admin ID
    if not ADMIN_IDS:
        ADMIN_IDS = [5952409238, 5498111784]  # Default admin IDs
except Exception:
    ADMIN_IDS = [5952409238, 5498111784]  # Default admin IDs

# Authorized contacts for adding scores
AUTHORIZED_CONTACTS = []
authorized_contacts_str = os.getenv("AUTHORIZED_CONTACTS", "")
if authorized_contacts_str:
    AUTHORIZED_CONTACTS = [contact.strip() for contact in authorized_contacts_str.split(",")]

# Modern emoji set for UI
EMOJI = {
    'welcome': '🚀',           # More tech-focused welcome
    'question': '❓',
    'open': '📱',              # More modern icon for open questions
    'help': '🔍',              # Search icon for help
    'rating': '📊',
    'cancel': '✖️',            # Bolder cancel
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'add': '➕',
    'check': '🔄',             # Refresh icon for checking
    'pin': '📍',               # Modern pin
    'description': '📝',
    'author': '👤',
    'time': '⏱️',              # Modern timer
    'status': '🔵',            # Status dot
    'open_status': '🟢',       # Green for open
    'closed_status': '🔴',     # Red for closed
    'online': '💬',            # Chat bubble for online
    'offline': '🤝',           # Handshake for meeting
    'mail': '📨',              # Modern mail
    'target': '🎯',
    'trophy': '🏆',
    'empty': '🔍',             # Search for empty
    'calendar': '📅',
    'info': 'ℹ️',
    'sos': '🆘',
    'open_questions': '📱',
    'admin': '⚙️',             # Gear for admin
    'contact': '👥',           # Contact icon
    'authorized': '🔐',        # Lock for authorized
    'unauthorized': '🔒',      # Locked for unauthorized
    'class': '🏫',             # School for class
    'points': '💯',            # Points
    'refresh': '🔄',           # Refresh
    'settings': '⚙️',          # Settings
    'back': '◀️',              # Back button
}

# UI Text constants
TEXT = {
    'welcome': f"{EMOJI['welcome']} <b>Добро пожаловать в AcadeMix</b> {EMOJI['welcome']}",
    'admin_welcome': f"{EMOJI['admin']} <b>Панель администратора AcadeMix</b> {EMOJI['settings']}",
    'help_title': f"{EMOJI['help']} <b>Справка по боту</b>",
    'rating_title': f"{EMOJI['trophy']} <b>Рейтинг классов</b>",
    'empty_rating': f"{EMOJI['empty']} Рейтинг пока пуст",
    'question_title': f"{EMOJI['pin']} <b>Введите заголовок вопроса</b>",
    'question_desc': f"{EMOJI['description']} <b>Введите описание вопроса</b>",
    'no_questions': f"{EMOJI['empty']} <b>Нет открытых вопросов</b>",
    'open_questions': f"{EMOJI['open']} <b>Открытые вопросы</b>",
    'action_cancelled': f"{EMOJI['cancel']} <b>Действие отменено</b>",
    'use_menu': f"{EMOJI['info']} Используйте меню для навигации",
    'add_points': f"{EMOJI['add']} <b>Добавление баллов</b>",
    'points_format': f"{EMOJI['info']} Введите в формате: <code>Класс Баллы</code>\nПример: <code>10A 50</code>",
    'points_added': f"{EMOJI['success']} Баллы успешно добавлены!",
    'unauthorized': f"{EMOJI['unauthorized']} У вас нет прав для этого действия",
    'contact_added': f"{EMOJI['success']} Контакт успешно добавлен в список авторизованных",
    'contact_exists': f"{EMOJI['info']} Этот контакт уже авторизован",
    'contact_removed': f"{EMOJI['success']} Контакт удален из списка авторизованных",
    'contact_not_found': f"{EMOJI['error']} Контакт не найден в списке авторизованных",
    'db_check_success': f"{EMOJI['success']} База данных в порядке",
    'db_check_error': f"{EMOJI['error']} Ошибка при проверке базы данных",
}