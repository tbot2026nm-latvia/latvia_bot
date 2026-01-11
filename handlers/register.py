from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import uuid
from services.db import create_user

router = Router()

class RegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()

@router.callback_query(F.data == "start_register")
async def start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Ismingizni kiriting:")
    await state.set_state(RegisterState.first_name)

@router.message(RegisterState.first_name)
async def f1(m: Message, s: FSMContext):
    await s.update_data(first_name=m.text)
    await m.answer("Familiyangiz:")
    await s.set_state(RegisterState.last_name)

@router.message(RegisterState.last_name)
async def f2(m: Message, s: FSMContext):
    await s.update_data(last_name=m.text)
    await m.answer("Telefon raqamingiz:")
    await s.set_state(RegisterState.phone)

@router.message(RegisterState.phone)
async def f3(m: Message, s: FSMContext):
    await s.update_data(phone=m.text)
    await m.answer("Pasport rasmini yuboring:")
    await s.set_state(RegisterState.passport)

@router.message(RegisterState.passport, F.photo)
async def f4(m: Message, s: FSMContext):
    data = await s.get_data()

    await create_user(
        m.from_user.id,
        data["first_name"],
        data["last_name"],
        data["phone"],
        "passport.jpg"
    )

    await m.answer("Maʼlumotlaringiz qabul qilindi. Admin tekshiradi.")
    await s.clear()
