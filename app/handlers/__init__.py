from aiogram import Router

from .admin_handlers import admin_router
from .user_handlers import user_router

main_router = Router()
main_router.include_routers(user_router, admin_router)