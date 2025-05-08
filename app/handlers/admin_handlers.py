from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.ui import UI
from ..text import UserText, EMOJI
from ..config import CLASS_DB_PATH
from ..utils import PermissionCheck
from ..fsm_states import PointsStates
from ..middlewares.admin_middleware import AdminMiddleware
import os
import aiosqlite
from ..services import ClassRatingService

admin_router = Router()
admin_router.message.middleware(AdminMiddleware())

@admin_router.message(F.text == f"{EMOJI['add']} Добавить баллы")
async def admin_add(message: Message, state: FSMContext):
    await message.answer(UserText.input_points, reply_markup=UI.cancel_button())
    await state.set_state(PointsStates.points)

@admin_router.message(PointsStates.points)
async def process_score(message: Message, state: FSMContext):
    if not await PermissionCheck.is_bot_admin(message):
        await state.clear()
        return
    if message.text == f"{EMOJI['cancel']} Отмена":
        await state.clear()
        await message.answer(UserText.cancelled, reply_markup=UI.admin_menu())
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(UserText.invalid_points_error, reply_markup=UI.admin_menu())
        await state.clear()
        return
    class_name, score = parts
    try:
        score = int(score)
    except ValueError:
        await message.answer(UserText.points_are_not_int_instance, reply_markup=UI.admin_menu())
        await state.clear()
    else:
        success = await ClassRatingService.add_class_score(class_name, score)
        if success:
            await message.answer(await UserText.process_scores_text(class_name, score), reply_markup=UI.admin_menu())
        else:
            await message.answer(UserText.adding_points_error, reply_markup=UI.admin_menu())
            await state.clear()

@admin_router.message(F.text == f"{EMOJI['check']} Проверить БД")
async def admin_check_db(message: Message):
    if not os.path.exists(CLASS_DB_PATH):
        await message.answer(f"❌ Файл базы данных не найден по пути: {CLASS_DB_PATH}", reply_markup=UI.admin_menu())
    else:
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