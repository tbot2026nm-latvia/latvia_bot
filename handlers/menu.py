from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from services.db import get_user, get_user_queue

router = Router()

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Navbat qo‘shish")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="📈 Status")]
        ],
        resize_keyboard=True
    )


@router.message(lambda m: m.text == "👤 Profil")
async def profile(msg: Message):
    user = await get_user(msg.from_user.id)
    await msg.answer(
        f"👤 {user['first_name']} {user['last_name']}\n📱 {user['phone']}\n📌 Status: {user['status']}",
        reply_markup=main_menu()
    )


@router.message(lambda m: m.text == "📈 Status")
async def status(msg: Message):
    rows = await get_user_queue(msg.from_user.id)

    if not rows:
        await msg.answer("📭 Sizda navbat yo‘q.", reply_markup=main_menu())
        return

    text = "📊 Sizning monitoringlar:\n\n"
    for r in rows:
        text += f"{r['service']} | {r['location']} | {r['status']}\n"

    await msg.answer(text, reply_markup=main_menu())
