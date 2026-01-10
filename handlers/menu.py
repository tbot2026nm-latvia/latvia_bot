from aiogram import Router
from aiogram.types import Message
from services.db import get_user

router = Router()

@router.message(lambda m: m.text == "📋 Mening holatim")
async def status(msg: Message):
    user = await get_user(msg.from_user.id)
    if not user:
        await msg.answer("Siz ro‘yxatdan o‘tmagansiz")
        return
    if user["status"] != "approved":
        await msg.answer("⏳ Admin tasdiqlashini kutyapsiz")
    else:
        await msg.answer(
            f"✅ Tasdiqlangan\nNavbat: {user['queue_number']}\nSana: {user['visit_date']}"
        )
