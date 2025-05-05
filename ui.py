from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple, Dict
from config import EMOJI

class UI:
    @staticmethod
    def main_menu():
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=f'{EMOJI["question"]} Задать вопрос'),
                    KeyboardButton(text=f'{EMOJI["open"]} Открытые вопросы')
                ],
                [
                    KeyboardButton(text=f'{EMOJI["rating"]} Рейтинг классов'),
                    KeyboardButton(text=f'{EMOJI["help"]} Помощь')
                ]
            ],
            resize_keyboard=True
        )
    @staticmethod
    def admin_menu():
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=f'{EMOJI["add"]} Добавить баллы'),
                    KeyboardButton(text=f'{EMOJI["rating"]} Рейтинг классов')
                ],
                [
                    KeyboardButton(text=f'{EMOJI["check"]} Проверить БД')
                ]
            ],
            resize_keyboard=True
        )
    @staticmethod
    def cancel_button():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=f"{EMOJI['cancel']} Отмена")]
            ],
            resize_keyboard=True
        )
    @staticmethod
    def answer_type_buttons(qid: int):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{EMOJI['online']} Ответить в Telegram", callback_data=f"answer_online_{qid}")],
                [InlineKeyboardButton(text=f"{EMOJI['offline']} Встреча", callback_data=f"answer_offline_{qid}")]
            ]
        )
    @staticmethod
    def question_list(questions: List[Tuple]):
        inline_keyboard = []
        for q in questions:
            text = q[1]
            # Обрезаем длинные заголовки вопросов до 50 символов для компактности
            if len(text) > 50:
                text = text[:47] + '...'
            inline_keyboard.append(
                [InlineKeyboardButton(text=f"{EMOJI['pin']} {text}", callback_data=f"question_{q[0]}")]
            )
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    @staticmethod
    def help_button():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Перейти к помощнику", url="https://t.me/AcadeMix_Support_bot")]
            ]
        )
    @staticmethod
    def format_class_rating(scores: List[Tuple]) -> str:
        text = f"{EMOJI['trophy']} <b>Рейтинг классов:</b>\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for idx, (cls, score) in enumerate(scores, 1):
            # Первым трём классам присваиваются медали, остальным — номер
            if idx <= 3 and idx <= len(medals):
                prefix = f"{medals[idx-1]} "
            else:
                prefix = f"{idx}. "
            text += f"{prefix}<b>{cls}</b>: {score} баллов\n"
        return text
    @staticmethod
    def format_question(question: Dict, with_author: bool = False) -> str:
        text = f"<b>{question['title']}</b>\n\n"
        if question['description']:
            text += f"{question['description']}\n\n"
        text += f"{EMOJI['status']} Статус: "
        # Показываем статус вопроса с соответствующим эмодзи
        text += f"{EMOJI['open_status']} Открыт" if question['status'] == 'open' else f"{EMOJI['closed_status']} Закрыт"
        text += f"\n{EMOJI['time']} Создан: {question['created_at']}"
        if with_author:
            text += f"\n{EMOJI['author']} Автор: {question['author']}"
        return text
