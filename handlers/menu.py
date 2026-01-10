from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.db import get_user

router = Router()

@router.message(Command("menu"))
async def menu(msg: Message):
    user = await get_user(msg.from_user.id)
    if not user:
        await msg.answer("Avval ro‘yxatdan o‘ting /register")
        return

    if user["status"] != "approved":
        await msg.answer("⏳ Admin tasdiqlashini kuting")
        return

    await msg.answer("📋 MENYU\n1. Navbat\n2. Status")
