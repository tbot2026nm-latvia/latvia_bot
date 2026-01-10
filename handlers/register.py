from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from services.db import create_user
from config import ADMIN_ID

router = Router()

class Register(StatesGroup):
    first = State()
    last = State()
    phone = State()
    passport = State()

@router.message(Register.first)
async def first(msg: types.Message, state: FSMContext):
    await state.update_data(first=msg.text)
    await state.set_state(Register.last)
    await msg.answer("Familiyangiz:")

@router.message(Register.last)
async def last(msg: types.Message, state: FSMContext):
    await state.update_data(last=msg.text)
    await state.set_state(Register.phone)
    await msg.answer("📱 Telefon raqamni yuboring", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    ))

@router.message(Register.phone)
async def phone(msg: types.Message, state: FSMContext):
    if not msg.contact:
        return await msg.answer("❗️ Tugmani bosib yuboring")
    await state.update_data(phone=msg.contact.phone_number)
    await state.set_state(Register.passport)
    await msg.answer("🛂 Pasport JPG yuboring (≤1MB)", reply_markup=types.ReplyKeyboardRemove())

@router.message(Register.passport)
async def passport(msg: types.Message, state: FSMContext):
    if not msg.photo:
        return await msg.answer("Faqat JPG rasm")
    file_id = msg.photo[-1].file_id
    data = await state.get_data()

    await create_user(msg.from_user.id, data['first'], data['last'], data['phone'], file_id)

    await msg.bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi foydalanuvchi:\n{data['first']} {data['last']}\n📱 {data['phone']}",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ Approve", callback_data=f"ok_{msg.from_user.id}")],
            [types.InlineKeyboardButton(text="❌ Reject", callback_data=f"no_{msg.from_user.id}")]
        ])
    )

    await msg.answer("⏳ Admin tasdiqlashini kuting")
    await state.clear()
