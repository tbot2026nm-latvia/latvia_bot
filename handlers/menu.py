from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.db import get_user

router = Router()

# ==========================
# MAIN MENU
# ==========================
@router.callback_query(F.data == "open_menu")
async def open_menu(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Navbat qo‘shish", callback_data="add_menu")],
        [InlineKeyboardButton(text="📄 Profil", callback_data="profile")]
    ])

    await call.message.edit_text("📋 Asosiy menyu:", reply_markup=kb)
    await call.answer()


# ==========================
# ADD QUEUE
# ==========================
@router.callback_query(F.data == "add_menu")
async def add_queue(call: CallbackQuery):
    await call.message.edit_text(
        "📊 Navbat monitoringi yoqildi.\n\n"
        "Biz Latvia VFS va Elchixona navbatlarini tekshirib boramiz.\n"
        "Agar bo‘sh joy chiqsa sizga xabar beramiz."
    )
    await call.answer("Monitoring yoqildi")


# ==========================
# PROFILE
# ==========================
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    user = await get_user(call.from_user.id)

    if not user:
        await call.message.edit_text("❌ Profil topilmadi.")
        return

    text = (
        f"👤 Profilingiz:\n\n"
        f"Ism: {user['first_name']}\n"
        f"Familiya: {user['last_name']}\n"
        f"Telefon: {user['phone']}\n"
        f"Holat: {user['status']}"
    )

    await call.message.edit_text(text)
    await call.answer()
