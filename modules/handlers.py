from telebot import types
from telebot.types import Message, CallbackQuery
import re
from datetime import datetime

from modules.bot_instance import bot
from modules.database import (
    register_user, get_open_questions, get_question_details,
    save_question, save_online_answer, save_offline_answer,
    save_state, get_state, clear_state, class_db, user_db
)
from modules.permissions import (
    is_admin, is_authorized, get_all_authorized_contacts,
    add_contact, remove_contact
)
from modules.ui import UI
from modules.config import TEXT, EMOJI

# Константы для состояний пользователя
STATE_WAITING_TITLE = "waiting_title"
STATE_WAITING_DESCRIPTION = "waiting_description"
STATE_WAITING_POINTS = "waiting_points"
STATE_WAITING_CONTACT = "waiting_contact"
STATE_WAITING_MEETING_TIME = "waiting_meeting_time"
STATE_WAITING_ADD_CONTACT = "waiting_add_contact"
STATE_WAITING_REMOVE_CONTACT = "waiting_remove_contact"

def register_all_handlers():
    # Регистрация всех обработчиков сообщений
    register_command_handlers()
    register_message_handlers()
    register_callback_handlers()

def register_command_handlers():
    # Регистрация обработчиков команд
    bot.register_message_handler(cmd_start, commands=['start'], pass_bot=True)
    bot.register_message_handler(cmd_help, commands=['help'], pass_bot=True)
    bot.register_message_handler(cmd_admin, commands=['admin'], pass_bot=True)

def register_message_handlers():
    # Регистрация обработчиков текстовых сообщений
    bot.register_message_handler(
        ask_question, 
        func=lambda msg: msg.text and f'{EMOJI["question"]} Задать вопрос' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        show_open_questions, 
        func=lambda msg: msg.text and f'{EMOJI["open"]} Открытые вопросы' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        show_rating, 
        func=lambda msg: msg.text and f'{EMOJI["rating"]} Рейтинг классов' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        cmd_help, 
        func=lambda msg: msg.text and f'{EMOJI["help"]} Помощь' in msg.text,
        pass_bot=True
    )
    
    bot.register_message_handler(
        add_points, 
        func=lambda msg: msg.text and f'{EMOJI["add"]} Добавить баллы' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        manage_contacts, 
        func=lambda msg: msg.text and f'{EMOJI["contact"]} Управление контактами' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        check_db, 
        func=lambda msg: msg.text and f'{EMOJI["check"]} Проверить БД' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        back_to_main, 
        func=lambda msg: msg.text and f'{EMOJI["back"]} Вернуться' in msg.text,
        pass_bot=True
    )
    
    bot.register_message_handler(
        add_authorized_contact, 
        func=lambda msg: msg.text and f'{EMOJI["add"]} Добавить контакт' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        remove_authorized_contact, 
        func=lambda msg: msg.text and f'{EMOJI["cancel"]} Удалить контакт' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        list_authorized_contacts, 
        func=lambda msg: msg.text and f'{EMOJI["check"]} Список контактов' in msg.text,
        pass_bot=True
    )
    bot.register_message_handler(
        back_to_admin, 
        func=lambda msg: msg.text and f'{EMOJI["back"]} Назад' in msg.text,
        pass_bot=True
    )
    
    bot.register_message_handler(
        cancel_action, 
        func=lambda msg: msg.text and f'{EMOJI["cancel"]} Отмена' in msg.text,
        pass_bot=True
    )
    
    # Регистрация обработчиков для разных состояний пользователя
    bot.register_message_handler(
        process_question_title, 
        func=lambda msg: get_state(msg.from_user.id) == STATE_WAITING_TITLE,
        pass_bot=True
    )
    bot.register_message_handler(
        process_question_description, 
        func=lambda msg: get_state(msg.from_user.id) and get_state(msg.from_user.id).startswith(STATE_WAITING_DESCRIPTION),
        pass_bot=True
    )
    bot.register_message_handler(
        process_points, 
        func=lambda msg: get_state(msg.from_user.id) == STATE_WAITING_POINTS,
        pass_bot=True
    )
    bot.register_message_handler(
        process_contact, 
        func=lambda msg: get_state(msg.from_user.id) and get_state(msg.from_user.id).startswith(STATE_WAITING_CONTACT),
        pass_bot=True
    )
    bot.register_message_handler(
        process_meeting_time, 
        func=lambda msg: get_state(msg.from_user.id) and get_state(msg.from_user.id).startswith(STATE_WAITING_MEETING_TIME),
        pass_bot=True
    )
    bot.register_message_handler(
        process_add_contact, 
        func=lambda msg: get_state(msg.from_user.id) == STATE_WAITING_ADD_CONTACT,
        pass_bot=True
    )
    bot.register_message_handler(
        process_remove_contact, 
        func=lambda msg: get_state(msg.from_user.id) == STATE_WAITING_REMOVE_CONTACT,
        pass_bot=True
    )

def register_callback_handlers():
    # Регистрация обработчиков для кнопок
    bot.register_callback_query_handler(
        process_question_selection, 
        func=lambda call: call.data and call.data.startswith('question_'),
        pass_bot=True
    )
    bot.register_callback_query_handler(
        process_online_answer, 
        func=lambda call: call.data and call.data.startswith('answer_online_'),
        pass_bot=True
    )
    bot.register_callback_query_handler(
        process_offline_answer, 
        func=lambda call: call.data and call.data.startswith('answer_offline_'),
        pass_bot=True
    )

def cmd_start(message: Message, bot):
    # Обработка команды /start - начало работы с ботом
    user_id = message.from_user.id
    username = message.from_user.username
    
    register_user(user_id, username)
    
    clear_state(user_id)
    
    bot.send_message(
        user_id,
        UI.format_welcome_message(),
        reply_markup=UI.main_menu(),
        parse_mode='HTML'
    )

def cmd_help(message: Message, bot):
    # Отправка справочной информации
    bot.send_message(
        message.chat.id,
        UI.format_help_message(),
        reply_markup=UI.help_button(),
        parse_mode='HTML'
    )

def cmd_admin(message: Message, bot):
    # Вход в панель администратора
    user_id = message.from_user.id
    
    if is_admin(user_id):
        bot.send_message(
            user_id,
            UI.format_admin_welcome(),
            reply_markup=UI.admin_menu(),
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            user_id,
            f"{EMOJI['error']} У вас нет прав администратора",
            reply_markup=UI.main_menu(),
            parse_mode='HTML'
        )

def ask_question(message: Message, bot):
    # Начало процесса создания вопроса
    user_id = message.from_user.id
    
    save_state(user_id, STATE_WAITING_TITLE)
    
    bot.send_message(
        user_id,
        TEXT['question_title'],
        reply_markup=UI.cancel_button(),
        parse_mode='HTML'
    )

def show_open_questions(message: Message, bot):
    # Отображение списка открытых вопросов
    questions = get_open_questions()
    
    if not questions:
        bot.send_message(
            message.chat.id,
            TEXT['no_questions'],
            parse_mode='HTML'
        )
        return
    
    bot.send_message(
        message.chat.id,
        TEXT['open_questions'],
        reply_markup=UI.question_list(questions),
        parse_mode='HTML'
    )

def show_rating(message: Message, bot):
    # Отображение рейтинга классов
    global class_db
    from modules.database import init_databases, class_db
    
    if class_db is None:
        try:
            init_databases()
            if class_db is None:
                bot.send_message(
                    message.chat.id,
                    f"{EMOJI['error']} <b>Ошибка базы данных!</b> Не удалось инициализировать базу данных классов.",
                    parse_mode='HTML'
                )
                return
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"{EMOJI['error']} <b>Ошибка базы данных!</b> {str(e)}",
                parse_mode='HTML'
            )
            return
    
    scores = class_db.get_scores()
    
    bot.send_message(
        message.chat.id,
        UI.format_class_rating(scores),
        parse_mode='HTML'
    )

def add_points(message: Message, bot):
    # Начало процесса добавления баллов классу
    user_id = message.from_user.id
    username = message.from_user.username
    
    if not (is_admin(user_id) or is_authorized(username)):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        return
    
    save_state(user_id, STATE_WAITING_POINTS)
    
    bot.send_message(
        user_id,
        TEXT['add_points'] + "\n\n" + TEXT['points_format'],
        reply_markup=UI.cancel_button(),
        parse_mode='HTML'
    )

def manage_contacts(message: Message, bot):
    # Вход в меню управления контактами
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        return
    
    bot.send_message(
        user_id,
        f"{EMOJI['contact']} <b>Управление авторизованными контактами</b>",
        reply_markup=UI.contact_management_menu(),
        parse_mode='HTML'
    )

def check_db(message: Message, bot):
    # Проверка состояния базы данных
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        return
    
    try:
        user_db.execute("SELECT 1")
        class_db.get_scores()
        
        bot.send_message(
            user_id,
            TEXT['db_check_success'],
            parse_mode='HTML'
        )
    except Exception as e:
        bot.send_message(
            user_id,
            f"{TEXT['db_check_error']}: {str(e)}",
            parse_mode='HTML'
        )

def back_to_main(message: Message, bot):
    # Возврат в главное меню
    cmd_start(message, bot)

def add_authorized_contact(message: Message, bot):
    # Начало процесса добавления авторизованного контакта
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        return
    
    save_state(user_id, STATE_WAITING_ADD_CONTACT)
    
    bot.send_message(
        user_id,
        f"{EMOJI['add']} <b>Добавление авторизованного контакта</b>\n\n"
        f"Введите имя пользователя (с @ или без):",
        reply_markup=UI.cancel_button(),
        parse_mode='HTML'
    )

def remove_authorized_contact(message: Message, bot):
    # Начало процесса удаления авторизованного контакта
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        return
    
    save_state(user_id, STATE_WAITING_REMOVE_CONTACT)
    
    bot.send_message(
        user_id,
        f"{EMOJI['cancel']} <b>Удаление автори��ованного контакта</b>\n\n"
        f"Введите имя пользователя (с @ или без):",
        reply_markup=UI.cancel_button(),
        parse_mode='HTML'
    )

def list_authorized_contacts(message: Message, bot):
    # Отображение списка авторизованных контактов
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        return
    
    contacts = get_all_authorized_contacts()
    
    bot.send_message(
        user_id,
        UI.format_authorized_contacts(contacts),
        parse_mode='HTML'
    )

def back_to_admin(message: Message, bot):
    # Возврат в меню администратора
    cmd_admin(message, bot)

def process_question_title(message: Message, bot):
    # Обработка заголовка вопроса
    user_id = message.from_user.id
    title = message.text.strip()
    
    if not title:
        bot.send_message(
            user_id,
            f"{EMOJI['error']} Заголовок не может быть пустым. Попробуйте еще раз:",
            parse_mode='HTML'
        )
        return
    
    save_state(user_id, f"{STATE_WAITING_DESCRIPTION}:{title}")
    
    bot.send_message(
        user_id,
        f"{TEXT['question_desc']}\n\n"
        f"Чтобы пропустить описание, отправьте символ '-' или нажмите {EMOJI['cancel']} Отмена и начните заново.",
        reply_markup=UI.cancel_button(),
        parse_mode='HTML'
    )

def process_question_description(message: Message, bot):
    # Обработка описания вопроса и сохранение вопроса
    user_id = message.from_user.id
    description = message.text.strip()
    
    state_data = get_state(user_id)
    if not state_data or ':' not in state_data:
        bot.send_message(
            user_id,
            f"{EMOJI['error']} <b>Произошла ошибка!</b> Пожалуйста, начните создание вопроса заново.",
            reply_markup=UI.main_menu(),
            parse_mode='HTML'
        )
        clear_state(user_id)
        return
        
    title = state_data.split(':', 1)[1]
    
    if not description or description == '-':
        description = "Нет описания"
    
    question_id = save_question(user_id, title, description)
    
    clear_state(user_id)
    
    bot.send_message(
        user_id,
        f"{EMOJI['success']} <b>Вопрос успешно создан!</b>\n\n"
        f"<b>Заголовок:</b> {title}\n"
        f"<b>Описание:</b> {description if description != 'Нет описания' else 'Не указано'}\n\n"
        f"Ваш вопрос будет доступен в разделе \"Открытые вопросы\".",
        reply_markup=UI.main_menu(),
        parse_mode='HTML'
    )

def process_points(message: Message, bot):
    # Обработка добавления баллов классу
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text.strip()
    
    if not (is_admin(user_id) or is_authorized(username)):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        clear_state(user_id)
        return
    
    match = re.match(r'^([0-9]+[A-Za-zА-Яа-я]+)\s+([0-9]+)$', text)
    
    if not match:
        bot.send_message(
            user_id,
            f"{EMOJI['error']} <b>Неверный формат!</b>\n\n{TEXT['points_format']}",
            parse_mode='HTML'
        )
        return
    
    class_name = match.group(1)
    points = int(match.group(2))
    
    global class_db
    from modules.database import init_databases, class_db
    
    if class_db is None:
        try:
            init_databases()
            if class_db is None:
                bot.send_message(
                    user_id,
                    f"{EMOJI['error']} <b>Ошибка базы данных!</b> Не удалось инициализировать базу данных классов.",
                    parse_mode='HTML'
                )
                clear_state(user_id)
                return
        except Exception as e:
            bot.send_message(
                user_id,
                f"{EMOJI['error']} <b>Ошибка базы данных!</b> {str(e)}",
                parse_mode='HTML'
            )
            clear_state(user_id)
            return
    
    success = class_db.add_score(class_name, points)
    
    clear_state(user_id)
    
    if success:
        bot.send_message(
            user_id,
            f"{EMOJI['success']} <b>Баллы успешно добавлены!</b>\n\n"
            f"Класс: {class_name}\n"
            f"Баллы: +{points}",
            reply_markup=UI.admin_menu() if is_admin(user_id) else UI.main_menu(),
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            user_id,
            f"{EMOJI['error']} <b>Ошибка при добавлении баллов!</b>",
            reply_markup=UI.admin_menu() if is_admin(user_id) else UI.main_menu(),
            parse_mode='HTML'
        )

def process_contact(message: Message, bot):
    # Обработка контактной информации для онлайн-ответа
    user_id = message.from_user.id
    contact = message.text.strip()
    
    state_data = get_state(user_id)
    question_id = int(state_data.split(':', 1)[1]) if ':' in state_data else 0
    
    if not question_id:
        clear_state(user_id)
        bot.send_message(
            user_id,
            f"{EMOJI['error']} <b>Ошибка при обработке запроса!</b>",
            reply_markup=UI.main_menu(),
            parse_mode='HTML'
        )
        return
    
    save_online_answer(question_id, user_id, contact)
    
    question = get_question_details(question_id)
    
    clear_state(user_id)
    
    bot.send_message(
        user_id,
        f"{EMOJI['success']} <b>Ваш контакт отправлен автору вопроса!</b>",
        reply_markup=UI.main_menu(),
        parse_mode='HTML'
    )
    
    if question and question['author_id'] != user_id:
        bot.send_message(
            question['author_id'],
            f"{EMOJI['success']} <b>На ваш вопрос ответили!</b>\n\n"
            f"Вопрос: {question['title']}\n"
            f"Контакт для связи: {contact}",
            parse_mode='HTML'
        )

def process_meeting_time(message: Message, bot):
    # Обработка информации о встрече для офлайн-ответа
    user_id = message.from_user.id
    meeting_time = message.text.strip()
    
    state_data = get_state(user_id)
    question_id = int(state_data.split(':', 1)[1]) if ':' in state_data else 0
    
    if not question_id:
        clear_state(user_id)
        bot.send_message(
            user_id,
            f"{EMOJI['error']} <b>Ошибка при обработке запроса!</b>",
            reply_markup=UI.main_menu(),
            parse_mode='HTML'
        )
        return
    
    save_offline_answer(question_id, user_id, meeting_time)
    
    question = get_question_details(question_id)
    
    clear_state(user_id)
    
    bot.send_message(
        user_id,
        f"{EMOJI['success']} <b>Информация о встрече отправлена автору вопроса!</b>",
        reply_markup=UI.main_menu(),
        parse_mode='HTML'
    )
    
    if question and question['author_id'] != user_id:
        bot.send_message(
            question['author_id'],
            f"{EMOJI['success']} <b>На ваш вопрос ответили!</b>\n\n"
            f"Вопрос: {question['title']}\n"
            f"Предложенное время встречи: {meeting_time}",
            parse_mode='HTML'
        )

def process_add_contact(message: Message, bot):
    # Обработка добавления авторизованного контакта
    user_id = message.from_user.id
    contact = message.text.strip()
    
    if not is_admin(user_id):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        clear_state(user_id)
        return
    
    success = add_contact(contact)
    
    clear_state(user_id)
    
    if success:
        bot.send_message(
            user_id,
            TEXT['contact_added'],
            reply_markup=UI.contact_management_menu(),
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            user_id,
            TEXT['contact_exists'],
            reply_markup=UI.contact_management_menu(),
            parse_mode='HTML'
        )

def process_remove_contact(message: Message, bot):
    # Обработка удаления авторизованного контакта
    user_id = message.from_user.id
    contact = message.text.strip()
    
    if not is_admin(user_id):
        bot.send_message(
            user_id,
            TEXT['unauthorized'],
            parse_mode='HTML'
        )
        clear_state(user_id)
        return
    
    success = remove_contact(contact)
    
    clear_state(user_id)
    
    if success:
        bot.send_message(
            user_id,
            TEXT['contact_removed'],
            reply_markup=UI.contact_management_menu(),
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            user_id,
            TEXT['contact_not_found'],
            reply_markup=UI.contact_management_menu(),
            parse_mode='HTML'
        )

def process_question_selection(call: CallbackQuery, bot):
    # Обработка выбора вопроса из списка
    user_id = call.from_user.id
    
    question_id = int(call.data.split('_')[1])
    
    question = get_question_details(question_id)
    
    if not question:
        bot.answer_callback_query(call.id, "Вопрос не найден")
        return
    
    text = UI.format_question(question, with_author=True)
    
    if question['status'] == 'open':
        bot.send_message(
            user_id,
            text,
            reply_markup=UI.answer_type_buttons(question_id),
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            user_id,
            text,
            parse_mode='HTML'
        )
    
    bot.answer_callback_query(call.id)

def process_online_answer(call: CallbackQuery, bot):
    # Начало процесса ответа онлайн
    user_id = call.from_user.id
    
    question_id = int(call.data.split('_')[2])
    
    save_state(user_id, f"{STATE_WAITING_CONTACT}:{question_id}")
    
    bot.send_message(
        user_id,
        f"{EMOJI['online']} <b>Ответ через Telegram</b>\n\n"
        f"Введите контактную информацию для связи (например, @username или номер телефона):",
        reply_markup=UI.cancel_button(),
        parse_mode='HTML'
    )
    
    bot.answer_callback_query(call.id)

def process_offline_answer(call: CallbackQuery, bot):
    # Начало процесса ответа офлайн
    user_id = call.from_user.id
    
    question_id = int(call.data.split('_')[2])
    
    save_state(user_id, f"{STATE_WAITING_MEETING_TIME}:{question_id}")
    
    bot.send_message(
        user_id,
        f"{EMOJI['offline']} <b>Личная встреча</b>\n\n"
        f"Введите предлагаемое время и место встречи:",
        reply_markup=UI.cancel_button(),
        parse_mode='HTML'
    )
    
    bot.answer_callback_query(call.id)

def cancel_action(message: Message, bot):
    # Отмена действия
    user_id = message.from_user.id
    
    clear_state(user_id)
    
    bot.send_message(
        user_id,
        TEXT['action_cancelled'],
        reply_markup=UI.main_menu(),
        parse_mode='HTML'
    )