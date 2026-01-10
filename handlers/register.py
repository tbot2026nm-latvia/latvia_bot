from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states import Register
from services.db import create_user
from config import ADMIN_ID

router = Router()

@router.message(Register.first_name)
async def first(message: types.Message, state: FSMContext):
    await state.update_data(first=message.text)
    await message.answer("👤 Familiyangizni kiriting:")
    await state.set_state(Register.last_name)

@router.message(Register.last_name)
async def last(message: types.Message, state: FSMContext):
    await state.update_data(last=message.text)

    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)]],
        resize_keyboard=True
    )

    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=kb)
    await state.set_state(Register.phone)

@router.message(Register.phone)
async def phone(message: types.Message, state: FSMContext):
    if not message.contact:
        await message.answer("❗ Tugma orqali yuboring")
        return

    await state.update_data(phone=message.contact.phone_number)
    await message.answer("🛂 Pasport JPG yuklang", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Register.passport)

@router.message(Register.passport)
async def passport(message: types.Message, state: FSMContext, bot):
    if not message.photo:
        await message.answer("❗ JPG rasm yuboring")
        return

    data = await state.get_data()
    file = message.photo[-1].file_id

    await create_user(message.from_user.id, data["first"], data["last"], data["phone"], file)

    await bot.send_photo(
        ADMIN_ID,
        file,
        caption=f"🆕 Ariza\n{data['first']} {data['last']}\n{data['phone']}\nID: {message.from_user.id}",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{message.from_user.id}"),
                    types.InlineKeyboardButton("❌ Rad", callback_data=f"no_{message.from_user.id}")
                ]
            ]
        )
    )

    await message.answer("⏳ Admin tekshirayotgan...")
    await state.set_state(Register.waiting_admin)
