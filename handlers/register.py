from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import uuid

from services.db import create_user, update_user_status
from config import ADMIN_ID

router = Router()

# ============================
# FSM
# ============================
class RegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()


# ============================
# CALLBACK FROM START SCREEN
# ============================
@router.callback_query(F.data == "start_register")
async def start_register_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(RegisterState.first_name)
    await call.message.edit_text("👤 Ismingizni kiriting:")
    await call.answer()


# ============================
# /register (backup)
# ============================
@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegisterState.first_name)
    await message.answer("👤 Ismingizni kiriting:")


# ============================
# FIRST NAME
# ============================
@router.message(RegisterState.first_name)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(RegisterState.last_name)
    await message.answer("👤 Familiyangizni kiriting:")


# ============================
# LAST NAME
# ============================
@router.message(RegisterState.last_name)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await state.set_state(RegisterState.phone)
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=kb)


# ============================
# PHONE
# ============================
@router.message(RegisterState.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Faqat o‘zingizning raqamingizni yuboring.")
        return

    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegisterState.passport)

    await message.answer(
        "🛂 Pasportingiz rasmini yuboring (JPG, 1MB gacha).",
        reply_markup=ReplyKeyboardRemove()
    )


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
        await message.answer("❌ Fayl 1MB dan katta.")
        return

    data = await state.get_data()
    passport_name = f"{uuid.uuid4()}.jpg"

    await create_user(
        telegram_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        passport_file=passport_name,
    )

    await message.answer("⏳ Ma’lumotlaringiz yuborildi. Admin tekshiradi.")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve:{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject:{message.from_user.id}")
        ]]
    )

    await message.bot.send_photo(
        ADMIN_ID,
        photo=photo.file_id,
        caption=(
            f"🆕 Yangi ro‘yxat:\n\n"
            f"👤 {data['first_name']} {data['last_name']}\n"
            f"📱 {data['phone']}\n"
            f"🆔 {message.from_user.id}"
        ),
        reply_markup=kb
    )

    await state.clear()


@router.message(RegisterState.passport)
async def wrong_passport(message: Message):
    await message.answer("❗ Pasportni rasm sifatida yuboring.")


# ============================
# ADMIN ACTIONS
# ============================
@router.callback_query(F.data.startswith("approve:"))
async def approve_user(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])

    await update_user_status(user_id, "approved")

    await call.message.edit_caption(call.message.caption + "\n\n✅ TASDIQLANDI")

    # USERGA MENU YUBORAMIZ
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Navbat qo‘shish", callback_data="open_menu")],
        [InlineKeyboardButton(text="📄 Profil", callback_data="profile")]
    ])

    await call.bot.send_message(
        user_id,
        "🎉 Siz admin tomonidan tasdiqlandingiz!\n\nEndi monitoringdan foydalanishingiz mumkin.",
        reply_markup=kb
    )

    await call.answer("Tasdiqlandi")


@router.callback_query(F.data.startswith("reject:"))
async def reject_user(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])
    await update_user_status(user_id, "rejected")
    await call.message.edit_caption(call.message.caption + "\n\n❌ RAD ETILDI")
    await call.bot.send_message(user_id, "❌ Siz rad etildingiz.")
    await call.answer("OK")
