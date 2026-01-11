from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import RegisterState
from services.db import create_user

router = Router()

ADMIN_ID = 5266262372


# ========== SURNAME ==========
@router.message(RegisterState.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegisterState.surname)
    await message.answer("👤 Familiyangizni kiriting:")


# ========== NAME ==========
router.callback_query(lambda c: c.data == "start_register")
async def start_register(call: CallbackQuery, state: FSMContext):
    await state.set_state(RegisterState.name)
    await call.message.edit_text("👤 Ismingizni kiriting:")
    await call.answer()

@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    await state.set_state(RegisterState.name)
    await message.answer("Ismingizni kiriting:")


# ========== PHONE ==========
@router.message(RegisterState.surname)
async def get_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(RegisterState.phone)
    await message.answer("📱 Telefon raqamingizni yuboring (Contact orqali):")
    
@router.message(RegisterState.phone)
async def wrong_phone(message: Message):
    await message.answer("❗ Telefonni tugma orqali yuboring (Contact)")


# ========== PASSPORT ==========
@router.message(RegisterState.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegisterState.passport)
    await message.answer("🛂 Pasport rasmini yuboring (jpg/png, 1MB dan kichik):")

@router.message(RegisterState.passport, F.photo)
async def get_passport(message: Message, state: FSMContext):
    data = await state.get_data()

    file_id = message.photo[-1].file_id

    # Save to DB
    await create_user(
        tg_id=message.from_user.id,
        name=data["name"],
        surname=data["surname"],
        phone=data["phone"],
        passport=file_id
    )

    # Send to admin
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
        ]
    ])

    caption = (
        "🆕 Yangi ro‘yxatdan o‘tish\n\n"
        f"👤 Ism: {data['name']}\n"
        f"👤 Familiya: {data['surname']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"🆔 Telegram ID: {message.from_user.id}"
    )

    await message.bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=caption,
        reply_markup=kb
    )

    await message.answer("⏳ Ma’lumotlaringiz adminga yuborildi.\nTasdiqlanishi kutilmoqda.")
    await state.clear()
