from aiogram import Router, F
from aiogram.types import Message
from services.db import get_pending_users, update_user_status
from config import ADMIN_ID

router = Router()

@router.message(F.text == "Admin")
async def admin_panel(m: Message):
    if m.from_user.id != ADMIN_ID:
        return

    users = await get_pending_users()

    if not users:
        await m.answer("Kutilayotgan foydalanuvchi yo‘q")
        return

    for u in users:
        await m.answer(
            f"{u['first_name']} {u['last_name']}\n{u['phone']}\nID: {u['telegram_id']}\n\n"
            f"/approve_{u['telegram_id']}  yoki  /reject_{u['telegram_id']}"
        )

@router.message(F.text.startswith("/approve_"))
async def approve(m: Message):
    uid = int(m.text.split("_")[1])
    await update_user_status(uid, "approved")
    await m.answer("Tasdiqlandi")

@router.message(F.text.startswith("/reject_"))
async def reject(m: Message):
    uid = int(m.text.split("_")[1])
    await update_user_status(uid, "rejected")
    await m.answer("Rad etildi")
