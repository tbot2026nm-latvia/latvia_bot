import os
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_ID = 5266262372

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ======================
# DATABASE
# ======================

async def get_db():
    return await asyncpg.connect(DATABASE_URL)

# ======================
# STATES
# ======================

class Register(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()

# ======================
# START
# ======================

@dp.message_handler(commands="start")
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Roziman", callback_data="agree"))
    await message.answer(
        "⚠️ *Bot qoidalari*\n\n"
        "• Ma’lumotlar tekshiriladi\n"
        "• Admin tasdiqlamasdan keyingi bosqich yo‘q\n\n"
        "Davom etish uchun rozilik bildiring.",
        parse_mode="Markdown",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data == "agree")
async def agree(call: types.CallbackQuery):
    await call.message.answer("Ismingizni kiriting:")
    await Register.first_name.set()

# ======================
# REGISTRATION
# ======================

@dp.message_handler(state=Register.first_name)
async def first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await Register.last_name.set()

@dp.message_handler(state=Register.last_name)
async def last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=kb)
    await Register.phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Register.phone)
async def phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("📄 Pasport rasmini yuboring (JPG, 1MB):",
                         reply_markup=types.ReplyKeyboardRemove())
    await Register.passport.set()

@dp.message_handler(content_types=types.ContentType.PHOTO, state=Register.passport)
async def passport(message: types.Message, state: FSMContext):
    data = await state.get_data()

    db = await get_db()
    await db.execute(
        """
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file)
        VALUES ($1, $2, $3, $4, $5)
        """,
        message.from_user.id,
        data["first_name"],
        data["last_name"],
        data["phone"],
        message.photo[-1].file_id
    )
    await db.close()

    await message.answer("⏳ Ma’lumotlaringiz admin tasdig‘iga yuborildi.")
    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi foydalanuvchi:\n"
        f"{data['first_name']} {data['last_name']}\n"
        f"📞 {data['phone']}\n\n"
        f"/approve_{message.from_user.id}"
    )
    await state.finish()

# ======================
# ADMIN APPROVE
# ======================

@dp.message_handler(lambda m: m.text.startswith("/approve_"))
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    user_id = int(message.text.split("_")[1])
    db = await get_db()
    await db.execute(
        "UPDATE users SET status='approved' WHERE telegram_id=$1",
        user_id
    )
    await db.close()

    await bot.send_message(user_id, "✅ Admin tasdiqladi. Siz navbat kuzatuvchisiz.")
    await message.answer("Tasdiqlandi ✅")

# ======================
# RUN
# ======================

if __name__ == "__main__":
    print("✅ BOT ISHGA TUSHDI (DB bilan)")
    executor.start_polling(dp, skip_updates=True)