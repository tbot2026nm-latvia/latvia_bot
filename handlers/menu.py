from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.db import add_queue, get_user_queue

router = Router()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Navbat qo‘shish", callback_data="menu_queue")],
        [InlineKeyboardButton(text="👤 Profil", callback_data="menu_profile")]
    ])

@router.callback_query(F.data == "menu_queue")
async def queue_start(call: CallbackQuery):
    await call.message.edit_text("⏳ Navbat yuklanmoqda...")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇱🇻 Riga VFS", callback_data="queue_riga")],
        [InlineKeyboardButton(text="🏛 Embassy", callback_data="queue_embassy")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_back")]
    ])
    await call.message.edit_text("📍 Qaysi xizmatni tanlaysiz?", reply_markup=kb)
    await call.answer()

@router.callback_query(F.data == "queue_riga")
async def queue_riga(call: CallbackQuery):
    await call.message.edit_text("🔍 Navbat qidirilmoqda...")
    await add_queue(call.from_user.id, "VFS", "Riga")
    await call.message.edit_text("🟢 Riga VFS navbati kuzatilyapti.\nSizga xabar beriladi.")
    await call.answer()

@router.callback_query(F.data == "queue_embassy")
async def queue_embassy(call: CallbackQuery):
    await call.message.edit_text("🔍 Elchixona navbati qidirilmoqda...")
    await add_queue(call.from_user.id, "Embassy", "Latvia")
    await call.message.edit_text("🟢 Elchixona navbati kuzatilyapti.")
    await call.answer()

@router.callback_query(F.data == "menu_profile")
async def profile(call: CallbackQuery):
    await call.message.edit_text(
        f"👤 Profil\n\nTelegram ID: {call.from_user.id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_back")]
        ])
    )
    await call.answer()

@router.callback_query(F.data == "menu_back")
async def back(call: CallbackQuery):
    await call.message.edit_text("🏠 Asosiy menu", reply_markup=main_menu())
    await call.answer()
