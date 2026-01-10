from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from services.db import add_user
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class Reg(StatesGroup):
    first = State()
    last = State()
    phone = State()
    passport = State()

@router.message(Command("register"))
async def start_reg(msg: Message, state: FSMContext):
    await msg.answer("Ismingizni kiriting:")
    await state.set_state(Reg.first)

@router.message(Reg.first)
async def first(msg: Message, state: FSMContext):
    await state.update_data(first=msg.text)
    await msg.answer("Familiyangizni kiriting:")
    await state.set_state(Reg.last)

@router.message(Reg.last)
async def last(msg: Message, state: FSMContext):
    await state.update_data(last=msg.text)
    await msg.answer("📱 Telefon raqamingizni yuboring (Contact):", reply_markup=None)
    await state.set_state(Reg.phone)

@router.message(Reg.phone)
async def phone(msg: Message, state: FSMContext):
    if not msg.contact:
        await msg.answer("❗ Tugma orqali yuboring")
        return
    await state.update_data(phone=msg.contact.phone_number)
    await msg.answer("🛂 Pasport JPG yuklang:")
    await state.set_state(Reg.passport)

@router.message(Reg.passport)
async def passport(msg: Message, state: FSMContext):
    if not msg.photo:
        await msg.answer("❗ Faqat rasm yuboring")
        return

    data = await state.get_data()
    file_id = msg.photo[-1].file_id

    await add_user(
        msg.from_user.id,
        data["first"],
        data["last"],
        data["phone"],
        file_id
    )

    await msg.answer("⏳ Admin tasdiqlashini kuting...")
    await state.clear()
