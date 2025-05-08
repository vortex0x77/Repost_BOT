from aiogram.types import Message

from .config import ADMIN_IDS

import dotenv, os


class ExcelSheets:
    ...


class PermissionCheck:
    @staticmethod
    async def is_bot_admin(event: Message) -> bool:
        return event.from_user.id in ADMIN_IDS

