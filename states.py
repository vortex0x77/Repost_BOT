from aiogram.fsm.state import State, StatesGroup

class QuestionStates(StatesGroup):
    waiting_for_title = State()         # Ожидание заголовка вопроса
    waiting_for_description = State()   # Ожидание описания вопроса

class AnswerStates(StatesGroup):
    waiting_for_contact = State()       # Ожидание контакта для онлайн ответа
    waiting_for_meeting_time = State()  # Ожидание времени для офлайн ответа
