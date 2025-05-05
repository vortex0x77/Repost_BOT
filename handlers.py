from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import QuestionStates, AnswerStates
from services import ClassRatingService, is_admin
from ui import UI
from config import EMOJI

router = Router()

@router.message(Command(commands=["start", "restart"]))
async def cmd_start(message: Message):
    uid = message.from_user.id
    if is_admin(uid):
        await message.answer("🛠 <b>Админ-меню</b>", reply_markup=UI.admin_menu())
    else:
        await ClassRatingService.register_user(uid, message.from_user.username or '')
        await message.answer(f"{EMOJI['welcome']} Добро пожаловать!", reply_markup=UI.main_menu())

@router.message(Command(commands=["help"]))
@router.message(F.text == f"{EMOJI['help']} Помощь")
async def cmd_help(message: Message):
    await message.answer(
        f"{EMOJI['sos']} <b>Справка по боту</b>\n\n"
        f"{EMOJI['question']} Задать вопрос — создать новый вопрос\n"
        f"{EMOJI['open_questions']} Открытые вопросы — список активных вопросов\n"
        f"{EMOJI['rating']} Рейтинг классов — просмотр рейтинга классов\n\n"
        f"Для связи с поддержкой: /help или кнопка ниже.",
        reply_markup=UI.help_button(),
        parse_mode="HTML"
    )

@router.message(F.text == f"{EMOJI['add']} Добавить баллы")
async def admin_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("📝 Введите в формате: <code>Класс Баллы</code>\nПример: 10A 50", 
                        parse_mode="HTML", reply_markup=UI.cancel_button())
    # Переводим FSM в режим ожидания ввода баллов (используем состояние для повторного использования шага)
    await state.set_state(AnswerStates.waiting_for_meeting_time)

@router.message(F.text == f"{EMOJI['check']} Проверить БД")
async def admin_check_db(message: Message):
    from services import CLASS_DB_PATH
    import os
    import aiosqlite
    if not is_admin(message.from_user.id):
        return
    if not os.path.exists(CLASS_DB_PATH):
        await message.answer(f"❌ Файл базы данных не найден по пути: {CLASS_DB_PATH}", 
                        reply_markup=UI.admin_menu())
        return
    async with aiosqlite.connect(CLASS_DB_PATH) as conn:
        cursor = await conn.execute("SELECT COUNT(*) FROM class_scores")
        count = (await cursor.fetchone())[0]
        cursor = await conn.execute("SELECT class_name, total_score FROM class_scores LIMIT 5")
        sample = await cursor.fetchall()
        text = f"✅ База данных в порядке\n📁 Путь: {CLASS_DB_PATH}\n📊 Количество классов: {count}\n\n"
        if sample:
            text += "Примеры записей:\n"
            for cls, score in sample:
                text += f"- {cls}: {score} баллов\n"
        await message.answer(text, reply_markup=UI.admin_menu())

@router.message(AnswerStates.waiting_for_meeting_time)
async def process_score(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    if message.text == f"{EMOJI['cancel']} Отмена":
        await state.clear()
        return await message.answer("Отменено", reply_markup=UI.admin_menu())
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Неверный формат. Нужно ввести класс и количество баллов.", reply_markup=UI.admin_menu())
        await state.clear()
        return
    class_name, score = parts
    try:
        score = int(score)
    except ValueError:
        await message.answer("❌ Баллы должны быть числом.", reply_markup=UI.admin_menu())
        await state.clear()
        return
    success = await ClassRatingService.add_class_score(class_name, score)
    if success:
        await message.answer(f"✅ Класс {class_name} получил +{score} баллов!", reply_markup=UI.admin_menu())
    else:
        await message.answer("⚠️ Произошла ошибка при добавлении баллов.", reply_markup=UI.admin_menu())
    await state.clear()

@router.message(F.text == f"{EMOJI['rating']} Рейтинг классов")
async def show_rating(message: Message):
    scores = await ClassRatingService.get_class_scores()
    if not scores:
        await message.answer("📊 Рейтинг пуст")
        return
    text = UI.format_class_rating(scores)
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == f'{EMOJI["question"]} Задать вопрос')
async def start_question(message: Message, state: FSMContext):
    await message.answer(
        f"{EMOJI['pin']} Введите краткий заголовок вопроса (до 100 символов):",
        reply_markup=UI.cancel_button()
    )
    # FSM: переводим в состояние ожидания заголовка вопроса
    await state.set_state(QuestionStates.waiting_for_title)

@router.message(QuestionStates.waiting_for_title)
async def process_question_title(message: Message, state: FSMContext):
    if message.text == f'{EMOJI["cancel"]} Отмена':
        await state.clear()
        return await message.answer(
            f"{EMOJI['info']} Создание вопроса отменено",
            reply_markup=UI.main_menu()
        )
    if len(message.text) > 100:
        return await message.reply(
            f"{EMOJI['warning']} Слишком длинный заголовок! Максимум 100 символов. Попробуйте еще раз:"
        )
    await state.update_data(title=message.text)
    await message.answer(
        f"{EMOJI['description']} Введите подробное описание вопроса (или отправьте '-' чтобы пропустить):"
    )
    # FSM: переводим в состояние ожидания описания вопроса
    await state.set_state(QuestionStates.waiting_for_description)

@router.message(QuestionStates.waiting_for_description)
async def process_question_description(message: Message, state: FSMContext):
    if message.text == f'{EMOJI["cancel"]} Отмена':
        await state.clear()
        return await message.answer(
            f"{EMOJI['info']} Создание вопроса отменено",
            reply_markup=UI.main_menu()
        )
    data = await state.get_data()
    title = data.get("title")
    description = message.text.strip()
    if description == "-":
        description = ""
    await ClassRatingService.save_question(message.from_user.id, title, description)
    await message.answer(
        f"{EMOJI['success']} Ваш вопрос отправлен!",
        reply_markup=UI.main_menu()
    )
    await state.clear()

@router.message(F.text == f"{EMOJI['open']} Открытые вопросы")
async def show_open_questions(message: Message):
    questions = await ClassRatingService.get_open()
    if not questions:
        await message.answer(f"{EMOJI['empty']} Нет открытых вопросов.", reply_markup=UI.main_menu())
        return
    await message.answer(
        f"{EMOJI['open']} <b>Открытые вопросы:</b>",
        reply_markup=UI.main_menu(),
        parse_mode="HTML"
    )
    await message.answer(
        "Выберите вопрос для просмотра:",
        reply_markup=UI.question_list(questions)
    )

@router.callback_query(F.data.startswith("question_"))
async def show_question_details(callback: CallbackQuery, state: FSMContext):
    # Получаем id вопроса из callback_data (например, "question_5" → 5)
    qid = int(callback.data.split("_")[1])
    question = await ClassRatingService.get_question(qid)
    if not question:
        await callback.message.answer(f"{EMOJI['error']} Вопрос не найден.", reply_markup=UI.main_menu())
        return
    await callback.message.answer(
        UI.format_question(question, with_author=True),
        reply_markup=UI.answer_type_buttons(qid),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("answer_online_"))
async def answer_online(callback: CallbackQuery, state: FSMContext):
    # Получаем id вопроса из callback_data (например, "answer_online_7" → 7)
    qid = int(callback.data.split("_")[-1])
    await state.update_data(qid=qid)
    await callback.message.answer(
        f"{EMOJI['mail']} Введите ваш Telegram-контакт (например, @username):",
        reply_markup=UI.cancel_button()
    )
    # FSM: переводим в состояние ожидания контакта
    await state.set_state(AnswerStates.waiting_for_contact)

@router.callback_query(F.data.startswith("answer_offline_"))
async def answer_offline(callback: CallbackQuery, state: FSMContext):
    # Получаем id вопроса из callback_data (например, "answer_offline_7" → 7)
    qid = int(callback.data.split("_")[-1])
    await state.update_data(qid=qid)
    await callback.message.answer(
        f"{EMOJI['calendar']} Введите дату и время встречи (например, 12.05 15:00):",
        reply_markup=UI.cancel_button()
    )
    # FSM: переводим в состояние ожидания времени встречи
    await state.set_state(AnswerStates.waiting_for_meeting_time)

@router.message(AnswerStates.waiting_for_contact)
async def process_online_answer(message: Message, state: FSMContext):
    if message.text == f"{EMOJI['cancel']} Отмена":
        await state.clear()
        return await message.answer("Отменено", reply_markup=UI.main_menu())
    if not message.text.startswith("@"):
        await message.answer("Пожалуйста, введите корректный Telegram-контакт (например, @username):")
        return
    data = await state.get_data()
    qid = data.get("qid")
    contact = message.text.strip()
    await ClassRatingService.save_online_answer(qid, message.from_user.id, contact)
    await message.answer(
        f"{EMOJI['success']} Ваш ответ отправлен автору вопроса!",
        reply_markup=UI.main_menu()
    )
    await state.clear()

@router.message(AnswerStates.waiting_for_meeting_time)
async def process_offline_answer(message: Message, state: FSMContext):
    if message.text == f"{EMOJI['cancel']} Отмена":
        await state.clear()
        return await message.answer("Отменено", reply_markup=UI.main_menu())
    data = await state.get_data()
    qid = data.get("qid")
    meeting_time = message.text.strip()
    await ClassRatingService.save_offline_answer(qid, message.from_user.id, meeting_time)
    await message.answer(
        f"{EMOJI['success']} Ваш ответ отправлен автору вопроса!",
        reply_markup=UI.main_menu()
    )
    await state.clear()