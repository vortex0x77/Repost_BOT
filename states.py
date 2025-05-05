from aiogram.fsm.state import State, StatesGroup

class QuestionStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()

class AnswerStates(StatesGroup):
    waiting_for_contact = State()
    waiting_for_meeting_time = State()