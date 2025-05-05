import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Пути к базам данных пользователей и классов
DB_PATH = os.getenv("USER_DB_PATH", "school_bot.db")
CLASS_DB_PATH = os.getenv("CLASS_DB_PATH", "classes.db")

# Список ID администраторов бота
ADMIN_IDS = []
admin_ids_str = os.getenv("ADMIN_ID", "1968139479")
try:
    # Преобразование строки с ID администраторов в список чисел
    for admin_id in admin_ids_str.replace(" ", "").split(","):
        if admin_id:
            ADMIN_IDS.append(int(admin_id))
    
    # Если список пуст, используем значения по умолчанию
    if not ADMIN_IDS:
        ADMIN_IDS = [5952409238, 5498111784]
except Exception:
    # При ошибке используем значения по умолчанию
    ADMIN_IDS = [5952409238, 5498111784]

# Список авторизованных контактов
AUTHORIZED_CONTACTS = []
authorized_contacts_str = os.getenv("AUTHORIZED_CONTACTS", "")
if authorized_contacts_str:
    # Преоб��азование строки контактов в список
    AUTHORIZED_CONTACTS = [contact.strip() for contact in authorized_contacts_str.split(",")]

# Словарь эмодзи для использования в сообщениях
EMOJI = {
    'welcome': '🚀',
    'question': '❓',
    'open': '📱',
    'help': '🔍',
    'rating': '📊',
    'cancel': '✖️',
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'add': '➕',
    'check': '🔄',
    'pin': '📍',
    'description': '📝',
    'author': '👤',
    'time': '⏱️',
    'status': '🔵',
    'open_status': '🟢',
    'closed_status': '🔴',
    'online': '💬',
    'offline': '🤝',
    'mail': '📨',
    'target': '🎯',
    'trophy': '🏆',
    'empty': '🔍',
    'calendar': '📅',
    'info': 'ℹ️',
    'sos': '🆘',
    'open_questions': '📱',
    'admin': '⚙️',
    'contact': '👥',
    'authorized': '🔐',
    'unauthorized': '🔒',
    'class': '🏫',
    'points': '💯',
    'refresh': '🔄',
    'settings': '⚙️',
    'back': '◀️',
}

# Словарь текстовых сообщений с форматированием и эмодзи
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
    'points_format': f"{EMOJI['info']} Введ��те в формате: <code>Класс Баллы</code>\nПример: <code>10A 50</code>",
    'points_added': f"{EMOJI['success']} Баллы успешно добавлены!",
    'unauthorized': f"{EMOJI['unauthorized']} У вас нет прав для этого действия",
    'contact_added': f"{EMOJI['success']} Контакт успешно добавлен в список авторизованных",
    'contact_exists': f"{EMOJI['info']} Этот контакт уже авторизован",
    'contact_removed': f"{EMOJI['success']} Контакт удален из списка авторизованных",
    'contact_not_found': f"{EMOJI['error']} Контакт не найден в списке авторизованных",
    'db_check_success': f"{EMOJI['success']} База данных в порядке",
    'db_check_error': f"{EMOJI['error']} Ошибка при проверке базы данных",
}