from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.db import get_pending, set_status
from config import ADMIN_ID

router = Router()

@router.message(Command("pending"))
async def pending(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return

    users = await get_pending()
    if not users:
        await msg.answer("Pending yo‘q")
        return

    for u in users:
        await msg.answer(
            f"{u['first_name']} {u['last_name']}\n{u['phone']}\n/approve_{u['telegram_id']}  /reject_{u['telegram_id']}"
        )

@router.message()
async def approve_reject(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return

    if msg.text.startswith("/approve_"):
        tg = int(msg.text.split("_")[1])
        await set_status(tg, "approved")
        await msg.answer("✅ Tasdiqlandi")

    if msg.text.startswith("/reject_"):
        tg = int(msg.text.split("_")[1])
        await set_status(tg, "rejected")
        await msg.answer("❌ Rad etildi")
