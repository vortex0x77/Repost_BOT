from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.ui import UI
from ..config import Settings
from ..text import UserText, EMOJI
from ..utils import PermissionCheck
from ..fsm_states import QuestionStates, AnswerStates

from ..services import ClassRatingService

user_router = Router()

@user_router.message(Command(commands=["start", "restart"]))
async def cmd_start(message: Message):
    uid = message.from_user.id
    if await PermissionCheck.is_bot_admin(message):
        await message.answer(UserText.admin_panel, reply_markup=UI.admin_menu())
    else:
        await ClassRatingService.register_user(uid, message.from_user.username or '')
        await message.answer(UserText.start_message, reply_markup=UI.main_menu())


@user_router.message(Command(commands=["help"]))
@user_router.message(F.text == f"{EMOJI['help']} Помощь")
async def cmd_help(message: Message):
    await message.answer(UserText.about, reply_markup=UI.help_button(),)


@user_router.message(F.text == f"{EMOJI['rating']} Рейтинг классов")
async def show_rating(message: Message):
    scores = await ClassRatingService.get_class_scores()
    if not scores:
        await message.answer(UserText.empty_rating)
    else:
        text = UI.format_class_rating(scores)
        await message.answer(text)


@user_router.message(F.text == f"{EMOJI['open']} Открытые вопросы")
async def show_open_questions(message: Message):
    questions = await ClassRatingService.get_open()
    if not questions:
        await message.answer(UserText.no_opened_questions, reply_markup=UI.main_menu())
    else:
        await message.answer(UserText.opened_questions, reply_markup=UI.main_menu())
        await message.answer(UserText.select_question, reply_markup=UI.question_list(questions))


@user_router.message(F.text == f'{EMOJI["question"]} Задать вопрос')
async def start_question(message: Message, state: FSMContext):
    await message.answer(UserText.input_question_title, reply_markup=UI.cancel_button())
    await state.set_state(QuestionStates.title)


@user_router.message(QuestionStates.title)
async def process_question_title(message: Message, state: FSMContext):
    if message.text == f'{EMOJI["cancel"]} Отмена':
        await state.clear()
        await message.answer(UserText.question_creation_cancelled, reply_markup=UI.main_menu())
    else:
        if len(message.text) > Settings.max_title_length:
            await message.reply(UserText.question_title_too_long)
        else:
            await state.update_data(title=message.text)
            await message.answer(UserText.input_question_desc)
            await state.set_state(QuestionStates.description)


@user_router.message(QuestionStates.description)
async def process_question_description(message: Message, state: FSMContext):
    if message.text == f'{EMOJI["cancel"]} Отмена':
        await state.clear()
        await message.answer(UserText.question_creation_cancelled, reply_markup=UI.main_menu())
    else:
        data = await state.get_data()
        title = data.get('title')
        description = message.text.strip()
        if description == '-':
            description = ''
        await ClassRatingService.save_question(message.from_user.id, title, description)
        await message.answer(UserText.question_sent_successfully, reply_markup=UI.main_menu())
        await state.clear()


@user_router.callback_query(F.data.startswith("question_"))
async def show_question_details(callback: CallbackQuery, state: FSMContext):
    # Получаем id вопроса из callback_data (например, "question_5" → 5)
    qid = int(callback.data.split("_")[1])
    question = await ClassRatingService.get_question(qid)
    if not question:
        await callback.message.answer(UserText.question_not_found, reply_markup=UI.main_menu())
    else:
        await callback.message.answer(UI.format_question(question, with_author=True), reply_markup=UI.answer_type_buttons(qid))


@user_router.callback_query(F.data.startswith("answer_online_"))
async def answer_online(callback: CallbackQuery, state: FSMContext):
    # Получаем id вопроса из callback_data (например, "answer_online_7" → 7)
    qid = int(callback.data.split("_")[-1])
    await state.update_data(qid=qid)
    await callback.message.answer(UserText.input_username, reply_markup=UI.cancel_button())
    await state.set_state(AnswerStates.contact)


@user_router.callback_query(F.data.startswith("answer_offline_"))
async def answer_offline(callback: CallbackQuery, state: FSMContext):
    # Получаем id вопроса из callback_data (например, "answer_offline_7" → 7)
    qid = int(callback.data.split('_')[-1])
    await state.update_data(qid=qid)
    await callback.message.answer(UserText.input_meeting_datetime, reply_markup=UI.cancel_button())
    await state.set_state(AnswerStates.meeting_time)


@user_router.message(AnswerStates.contact)
async def process_online_answer(message: Message, state: FSMContext):
    if message.text == f"{EMOJI['cancel']} Отмена":
        await state.clear()
        await message.answer(UserText.cancelled, reply_markup=UI.main_menu())
    else:
        if not message.text.startswith("@"):
            await message.answer(UserText.invalid_username)
        else:
            data = await state.get_data()
            qid = data.get("qid")
            contact = message.text.strip()
            await ClassRatingService.save_online_answer(qid, message.from_user.id, contact)
            await message.answer(UserText.answer_sent, reply_markup=UI.main_menu())
            await state.clear()


@user_router.message(AnswerStates.meeting_time)
async def process_offline_answer(message: Message, state: FSMContext):
    if message.text == f"{EMOJI['cancel']} Отмена":
        await state.clear()
        await message.answer(UserText.cancelled, reply_markup=UI.main_menu())
    else:
        data = await state.get_data()
        qid = data.get("qid")
        meeting_time = message.text.strip()
        await ClassRatingService.save_offline_answer(qid, message.from_user.id, meeting_time)
        await message.answer(UserText.answer_sent, reply_markup=UI.main_menu())
        await state.clear()

    

