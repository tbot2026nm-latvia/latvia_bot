from aiogram import Router
from aiogram.types import Message
from config import ADMIN_ID
from services.db import get_pending_users

router = Router()


@router.message(lambda m: m.text == "/admin" and m.from_user.id == ADMIN_ID)
async def admin_panel(msg: Message):
    users = await get_pending_users()

    if not users:
        await msg.answer("📭 Tasdiqlanmagan foydalanuvchi yo‘q.")
        return

    text = "🕒 Kutilayotgan foydalanuvchilar:\n\n"
    for u in users:
        text += f"{u['first_name']} {u['last_name']} | {u['phone']}\n"

    await msg.answer(text)
