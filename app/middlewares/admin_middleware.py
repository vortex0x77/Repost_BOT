from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware

from app.text import UserText
from app.utils import PermissionCheck

from typing import Callable, Awaitable, Dict, Any


class AdminMiddleware(BaseMiddleware):
    async def __call__(self, 
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]) -> Any: 
        
        if await PermissionCheck.is_bot_admin(event):
            return await handler(event, data)
        else:
            await event.answer(text=UserText.command_not_found)