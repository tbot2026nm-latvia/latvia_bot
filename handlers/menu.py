from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from services.db import get_user, add_queue, get_user_queue

router = Router()

def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Navbat"), KeyboardButton(text="➕ Qo‘shish")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="⚙️ Sozlamalar")]
        ],
        resize_keyboard=True
    )

@router.message(lambda m: m.text == "➕ Qo‘shish")
async def add(message: Message):
    await add_queue(message.from_user.id, "VFS", "Toshkent")
    await message.answer("⏳ Navbat qo‘shildi", reply_markup=menu())

@router.message(lambda m: m.text == "📊 Navbat")
async def navbat(message: Message):
    q = await get_user_queue(message.from_user.id)
    txt = "📊 Sizning navbatlaringiz:\n\n"
    for r in q:
        txt += f"{r['service']} - {r['location']} - {r['status']}\n"
    await message.answer(txt or "Bo‘sh", reply_markup=menu())

@router.message(lambda m: m.text == "👤 Profil")
async def profile(message: Message):
    u = await get_user(message.from_user.id)
    await message.answer(
        f"{u['first_name']} {u['last_name']}\n{u['phone']}\nStatus: {u['status']}",
        reply_markup=menu()
    )
