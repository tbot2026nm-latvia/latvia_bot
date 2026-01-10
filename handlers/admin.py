from aiogram import Router, F
from aiogram.types import Message
from services.db import get_pending_users, approve_user, get_approved_users, log_event

ADMIN_ID = 5266262372
router = Router()

def is_admin(msg):
    return msg.from_user.id == ADMIN_ID

@router.message(F.text == "/pending")
async def pending(msg: Message):
    if not is_admin(msg): return
    users = await get_pending_users()
    if not users:
        await msg.answer("✅ Pending yo‘q")
        return
    text = "⏳ Kutilayotganlar:\n\n"
    for u in users:
        text += f"{u['telegram_id']} | {u['first_name']} {u['last_name']}\n"
    await msg.answer(text)

@router.message(F.text.startswith("/approve"))
async def approve(msg: Message):
    if not is_admin(msg): return
    uid = int(msg.text.split()[1])
    q = await approve_user(uid)
    await log_event(uid, "APPROVED")
    await msg.answer(f"✅ {uid} tasdiqlandi. Navbati: {q}")

@router.message(F.text == "/users")
async def users(msg: Message):
    if not is_admin(msg): return
    users = await get_approved_users()
    text = "📋 Tasdiqlanganlar:\n"
    for u in users:
        text += f"{u['queue_number']} | {u['first_name']} {u['last_name']}\n"
    await msg.answer(text)

@router.message(F.text == "/stats")
async def stats(msg: Message):
    if not is_admin(msg): return
    p = len(await get_pending_users())
    a = len(await get_approved_users())
    await msg.answer(f"⏳ Pending: {p}\n✅ Approved: {a}")
