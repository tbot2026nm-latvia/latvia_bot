from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import RegisterState

router = Router()

@router.message(Command("register"))
async def start_register(message: Message, state: FSMContext):
    await state.set_state(RegisterState.name)
    await message.answer("Ismingizni kiriting:")

@router.message(RegisterState.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegisterState.surname)
    await message.answer("Familiyangizni kiriting:")

@router.message(RegisterState.surname)
async def get_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )

    await state.set_state(RegisterState.phone)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=kb)

@router.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer("Iltimos, tugma orqali yuboring.")
        return

    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegisterState.passport)
    await message.answer("📸 Pasport rasmini yuboring:")
