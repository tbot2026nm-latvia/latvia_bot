import os
import logging
import asyncpg

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils import executor

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 5266262372

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

db: asyncpg.Connection = None

# =====================
# FSM STATES
# =====================
class Register(StatesGroup):
    rules = State()
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()
    waiting_admin = State()

# =====================
# STARTUP
# =====================
async def on_startup(dp):
    global db
    db = await asyncpg.connect(DATABASE_URL)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            passport_file TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    logging.info("✅ Bot ishga tushdi")

# =====================
# /start
# =====================
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await state.finish()

    text = (
        "⚠️ *XAVFSIZLIK VA FOYDALANISH QOIDALARI*\n\n"
        "• Ma’lumotlar faqat rasmiy maqsadlarda ishlatiladi\n"
        "• Soxta ma’lumot taqiqlanadi\n"
        "• Pasport JPG ≤ 1MB bo‘lishi shart\n\n"
        "Davom etish uchun rozilik bildiring 👇"
    )

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Roziman", callback_data="agree_rules")
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=kb)
    await Register.rules.set()

# =====================
# RULES AGREE
# =====================
@dp.callback_query_handler(lambda c: c.data == "agree_rules", state=Register.rules)
async def agree_rules(call: types.CallbackQuery):
    await call.message.answer("✍️ Ismingizni kiriting:")
    await Register.first_name.set()

# =====================
# FIRST NAME
# =====================
@dp.message_handler(state=Register.first_name)
async def first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("✍️ Familiyangizni kiriting:")
    await Register.last_name.set()

# =====================
# LAST NAME
# =====================
@dp.message_handler(state=Register.last_name)
async def last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))

    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=kb)
    await Register.phone.set()

# =====================
# PHONE (CONTACT)
# =====================
@dp.message_handler(content_types=types.ContentType.CONTACT, state=Register.phone)
async def phone(message: types.Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ O‘zingizning raqamingizni yuboring!")
        return

    data = await state.get_data()

    await db.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (telegram_id) DO NOTHING
    """, message.from_user.id, data['first_name'], data['last_name'], message.contact.phone_number)

    await message.answer("🛂 Endi pasportingizni JPG formatda yuboring (≤1MB):",
                         reply_markup=types.ReplyKeyboardRemove())
    await Register.passport.set()

# =====================
# PASSPORT
# =====================
@dp.message_handler(content_types=types.ContentType.PHOTO, state=Register.passport)
async def passport(message: types.Message, state: FSMContext):
    photo = message.photo[-1]

    if photo.file_size > 1 * 1024 * 1024:
        await message.answer("❌ Fayl 1MB dan katta!")
        return

    await db.execute("""
        UPDATE users
        SET passport_file = $1
        WHERE telegram_id = $2
    """, photo.file_id, message.from_user.id)

    data = await state.get_data()

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve:{message.from_user.id}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{message.from_user.id}")
    )

    await bot.send_photo(
        ADMIN_ID,
        photo.file_id,
        caption=(
            "🛂 *YANGI FOYDALANUVCHI*\n\n"
            f"👤 {data['first_name']} {data['last_name']}\n"
            f"📞 {data['phone']}\n"
            f"🆔 {message.from_user.id}"
        ),
        parse_mode="Markdown",
        reply_markup=kb
    )

    await message.answer("✅ Ma’lumotlar yuborildi.\n⏳ Admin tasdiqlashini kuting.")
    await Register.waiting_admin.set()

# =====================
# ADMIN APPROVE / REJECT
# =====================
@dp.callback_query_handler(lambda c: c.data.startswith("approve:"))
async def approve(call: types.CallbackQuery):
    user_id = int(call.data.split(":")[1])

    await db.execute("""
        UPDATE users SET status='approved'
        WHERE telegram_id=$1
    """, user_id)

    await bot.send_message(user_id, "🎉 Siz tasdiqlandingiz! Endi xizmatlardan foydalanishingiz mumkin.")
    await call.message.edit_caption(call.message.caption + "\n\n✅ TASDIQLANDI")

@dp.callback_query_handler(lambda c: c.data.startswith("reject:"))
async def reject(call: types.CallbackQuery):
    user_id = int(call.data.split(":")[1])

    await db.execute("""
        UPDATE users SET status='rejected'
        WHERE telegram_id=$1
    """, user_id)

    await bot.send_message(user_id, "❌ Ma’lumotlaringiz rad etildi.")
    await call.message.edit_caption(call.message.caption + "\n\n❌ RAD ETILDI")

# =====================
# ADMIN COMMANDS
# =====================
@dp.message_handler(commands=['pending'])
async def pending(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    rows = await db.fetch("SELECT first_name, last_name FROM users WHERE status='pending'")
    text = "⏳ Kutilayotganlar:\n" + "\n".join(
        f"- {r['first_name']} {r['last_name']}" for r in rows
    ) if rows else "Yo‘q"

    await message.answer(text)

@dp.message_handler(commands=['users'])
async def users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    rows = await db.fetch("SELECT first_name, last_name, status FROM users")
    text = "\n".join(f"{r['first_name']} {r['last_name']} — {r['status']}" for r in rows)
    await message.answer(text or "Bo‘sh")

# =====================
# RUN
# =====================
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
