from telebot import types
from typing import List, Tuple, Dict, Any

from modules.config import EMOJI, TEXT

class UI:
    @staticmethod
    def main_menu():
        """Create main menu keyboard with modern styling"""
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            types.KeyboardButton(f'{EMOJI["question"]} Задать вопрос'),
            types.KeyboardButton(f'{EMOJI["open"]} Открытые вопросы')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["rating"]} Рейтинг классов'),
            types.KeyboardButton(f'{EMOJI["help"]} Помощь')
        )
        return kb

    @staticmethod
    def admin_menu():
        """Create admin menu keyboard with modern styling"""
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            types.KeyboardButton(f'{EMOJI["add"]} Добавить баллы'),
            types.KeyboardButton(f'{EMOJI["contact"]} Управление контактами')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["rating"]} Рейтинг классов'),
            types.KeyboardButton(f'{EMOJI["check"]} Проверить БД')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["back"]} Вернуться')
        )
        return kb

    @staticmethod
    def contact_management_menu():
        """Create contact management menu"""
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            types.KeyboardButton(f'{EMOJI["add"]} Добавить контакт'),
            types.KeyboardButton(f'{EMOJI["cancel"]} Удалить контакт')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["check"]} Список контактов'),
            types.KeyboardButton(f'{EMOJI["back"]} Назад')
        )
        return kb

    @staticmethod
    def cancel_button():
        """Create cancel button keyboard"""
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton(f"{EMOJI['cancel']} Отмена"))
        return kb

    @staticmethod
    def back_button():
        """Create back button keyboard"""
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton(f"{EMOJI['back']} Назад"))
        return kb

    @staticmethod
    def answer_type_buttons(qid: int):
        """Create answer type inline buttons"""
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton(
                f"{EMOJI['online']} Ответить в Telegram", 
                callback_data=f"answer_online_{qid}"
            ),
            types.InlineKeyboardButton(
                f"{EMOJI['offline']} Личная встреча", 
                callback_data=f"answer_offline_{qid}"
            )
        )
        return kb

    @staticmethod
    def question_list(questions: List[Tuple]):
        """Create question list inline keyboard"""
        kb = types.InlineKeyboardMarkup(row_width=1)
        for q in questions:
            text = q[1]
            if len(text) > 40:  # Shorter for modern UI
                text = text[:37] + '...'
            kb.add(types.InlineKeyboardButton(
                f"{EMOJI['pin']} {text}", 
                callback_data=f"question_{q[0]}"
            ))
        return kb

    @staticmethod
    def help_button():
        """Create help button inline keyboard"""
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            f"{EMOJI['sos']} Перейти к помощнику", 
            url="https://t.me/AcadeMix_Support_bot"
        ))
        return kb

    @staticmethod
    def format_welcome_message() -> str:
        """Format welcome message with modern styling"""
        return f"""
{TEXT['welcome']}

<b>Возможности бота:</b>
• {EMOJI['question']} Задавайте учебные вопросы
• {EMOJI['open']} Отвечайте на вопросы других учеников
• {EMOJI['rating']} Следите за рейтингом классов

<b>Используйте меню для навигации</b>
"""

    @staticmethod
    def format_admin_welcome() -> str:
        """Format admin welcome message"""
        return f"""
{TEXT['admin_welcome']}

<b>Доступные функции:</b>
• {EMOJI['add']} Добавление баллов классам
• {EMOJI['contact']} Управление авт��ризованными контактами
• {EMOJI['rating']} Просмотр рейтинга классов
• {EMOJI['check']} Проверка состояния базы данных

<b>Используйте меню для навигации</b>
"""

    @staticmethod
    def format_help_message() -> str:
        """Format help message with modern styling"""
        return f"""
{TEXT['help_title']}

<b>Основные функции:</b>
{EMOJI['question']} <b>Задать вопрос</b> - создать новый вопрос
{EMOJI['open']} <b>Открытые вопросы</b> - список активных вопросов
{EMOJI['rating']} <b>Рейтинг классов</b> - текущий рейтинг

<b>Команды:</b>
/start - перезапустить бота
/help - показать эту справку
"""

    @staticmethod
    def format_class_rating(scores: List[Tuple]) -> str:
        """Format class rating with modern styling"""
        if not scores:
            return TEXT['empty_rating']
            
        text = f"{TEXT['rating_title']}\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, (cls, score) in enumerate(scores, 1):
            if idx <= 3 and idx <= len(medals):
                prefix = f"{medals[idx-1]} "
            else:
                prefix = f"{idx}. "
            text += f"{prefix}<b>{cls}</b>: {score} {EMOJI['points']}\n"
            
        return text

    @staticmethod
    def format_question(question: Dict[str, Any], with_author: bool = False) -> str:
        """Format question details with modern styling"""
        text = f"<b>{question['title']}</b>\n\n"
        
        if question['description'] and question['description'] != 'Нет описания':
            text += f"{question['description']}\n\n"
        
        text += f"{EMOJI['status']} <b>Статус:</b> "
        text += f"{EMOJI['open_status']} Открыт" if question['status'] == 'open' else f"{EMOJI['closed_status']} Закрыт"
        text += f"\n{EMOJI['time']} <b>Создан:</b> {question['created_at']}"
        
        if with_author:
            text += f"\n{EMOJI['author']} <b>Автор:</b> {question['author']}"
            
        return text

    @staticmethod
    def format_authorized_contacts(contacts: List[str]) -> str:
        """Format authorized contacts list"""
        if not contacts:
            return f"{EMOJI['empty']} <b>Список авторизованных контактов пуст</b>"
            
        text = f"{EMOJI['authorized']} <b>Авторизованные контакты:</b>\n\n"
        for idx, contact in enumerate(contacts, 1):
            text += f"{idx}. {contact}\n"
            
        return text