from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import os
import uuid

from services.db import create_user, set_user_status
from config import ADMIN_ID

router = Router()


# ============================
# FSM States
# ============================
class RegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()


# ============================
# /register command
# ============================
@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👤 Ismingizni kiriting:")
    await state.set_state(RegisterState.first_name)


# ============================
# FIRST NAME
# ============================
@router.message(RegisterState.first_name)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("👤 Familiyangizni kiriting:")
    await state.set_state(RegisterState.last_name)


# ============================
# LAST NAME
# ============================
@router.message(RegisterState.last_name)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        "📱 Telefon raqamingizni yuboring (Telegram contact orqali):",
        reply_markup=kb,
    )
    await state.set_state(RegisterState.phone)


# ============================
# PHONE (CONTACT REQUIRED)
# ============================
@router.message(RegisterState.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Iltimos, o‘zingizning telefon raqamingizni yuboring.")
        return

    await state.update_data(phone=message.contact.phone_number)

    await message.answer(
        "🛂 Endi pasportingizning fotosuratini yuboring (JPG, 1MB dan kichik).",
        reply_markup=None,
    )
    await state.set_state(RegisterState.passport)


@router.message(RegisterState.phone)
async def wrong_phone(message: Message):
    await message.answer("❗ Telefonni faqat tugma orqali yuboring.")


# ============================
# PASSPORT
# ============================
@router.message(RegisterState.passport, F.photo)
async def get_passport(message: Message, state: FSMContext):
    photo = message.photo[-1]

    if photo.file_size > 1_000_000:
        await message.answer("❌ Fayl 1MB dan katta. Kichikroq rasm yuboring.")
        return

    file_id = photo.file_id

    data = await state.get_data()

    passport_name = f"{uuid.uuid4()}.jpg"

    await create_user(
        telegram_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        passport_file=passport_name,
    )

    await message.answer(
        "⏳ Ma’lumotlaringiz qabul qilindi.\nAdmin tasdiqlashini kuting."
    )

    # Send to admin
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve:{message.from_user.id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"reject:{message.from_user.id}",
                ),
            ]
        ]
    )

    await message.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption=(
            f"🆕 Yangi ro‘yxatdan o‘tish:\n\n"
            f"👤 {data['first_name']} {data['last_name']}\n"
            f"📱 {data['phone']}\n"
            f"🆔 Telegram ID: {message.from_user.id}"
        ),
        reply_markup=kb,
    )

    await state.clear()


@router.message(RegisterState.passport)
async def wrong_passport(message: Message):
    await message.answer("❗ Iltimos, pasport rasmini yuboring (foto).")


# ============================
# ADMIN APPROVE / REJECT
# ============================
@router.callback_query(F.data.startswith("approve:"))
async def approve_user(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])

    await set_user_status(user_id, "approved")
    await call.message.edit_caption(call.message.caption + "\n\n✅ TASDIQLANDI")
    await call.bot.send_message(user_id, "🎉 Admin sizni tasdiqladi! Endi botdan foydalanishingiz mumkin.")
    await call.answer("Tasdiqlandi")


@router.callback_query(F.data.startswith("reject:"))
async def reject_user(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])

    await set_user_status(user_id, "rejected")
    await call.message.edit_caption(call.message.caption + "\n\n❌ RAD ETILDI")
    await call.bot.send_message(user_id, "❌ Ro‘yxatdan o‘tish rad etildi.")
    await call.answer("Rad etildi")
