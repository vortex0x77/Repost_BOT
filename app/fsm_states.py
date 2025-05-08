from aiogram.fsm.state import State, StatesGroup
class QuestionStates(StatesGroup):
    title       = State()  
    description = State()   

class AnswerStates(StatesGroup):
    contact      = State()      
    meeting_time = State()

class PointsStates(StatesGroup):
    points = State()