from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.db import pool, is_user_approved
from aiogram.types import CallbackQuery
from aiogram import F

router = Router()

@router.callback_query(F.data == "open_menu")
async def open_menu(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Navbat qo‘shish", callback_data="add_menu")],
        [InlineKeyboardButton(text="📄 Profil", callback_data="profile")]
    ])

    await call.message.edit_text("📋 Asosiy menyu:", reply_markup=kb)
    await call.answer()

@router.message(F.text == "📊 Navbat qo‘shish")
async def add_queue(message: Message):
    if not await is_user_approved(message.from_user.id):
        await message.answer("⛔ Avval admin tasdiqlashi kerak.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="VFS Riga", callback_data="add:VFS:Riga")],
        [InlineKeyboardButton(text="Elchixona", callback_data="add:EMBASSY:Riga")]
    ])
    await message.answer("Xizmatni tanlang:", reply_markup=kb)


@router.callback_query(F.data.startswith("add:"))
async def add(call):
    _, service, location = call.data.split(":")

    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO queue (user_id, service, location) VALUES ($1,$2,$3)",
            call.from_user.id, service, location
        )

    await call.message.edit_text("⏳ Monitoringga qo‘shildi.")
    await call.answer()
