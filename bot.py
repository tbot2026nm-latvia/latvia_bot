import os
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_ID = 5266262372

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

db: asyncpg.Pool = None


# ================= DB =================

async def init_db():
    global db
    db = await asyncpg.create_pool(DATABASE_URL)


# ================= FSM =================

class RegisterFSM(StatesGroup):
    rules = State()
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()


# ================= KEYBOARDS =================

agree_kb = ReplyKeyboardMarkup(resize_keyboard=True)
agree_kb.add(KeyboardButton("✅ Roziman"))

contact_kb = ReplyKeyboardMarkup(resize_keyboard=True)
contact_kb.add(KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True))


# ================= START =================

@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await RegisterFSM.rules.set()
    await message.answer(
        "🔐 *XAVFSIZLIK VA QOIDALAR*\n\n"
        "• Maʼlumotlaringiz himoyalanadi\n"
        "• Passport JPG (≤1MB)\n"
        "• Admin tasdiqlamaguncha bot ishlamaydi\n\n"
        "Davom etish uchun rozilik bildiring.",
        parse_mode="Markdown",
        reply_markup=agree_kb
    )


@dp.message_handler(lambda m: m.text == "✅ Roziman", state=RegisterFSM.rules)
async def rules_ok(message: types.Message):
    await RegisterFSM.first_name.set()
    await message.answer("👤 Ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=RegisterFSM.first_name)
async def first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await RegisterFSM.last_name.set()
    await message.answer("👤 Familiyangizni kiriting:")


@dp.message_handler(state=RegisterFSM.last_name)
async def last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await RegisterFSM.phone.set()
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=contact_kb)


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegisterFSM.phone)
async def phone(message: types.Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Faqat o‘zingizning raqamingizni yuboring")
        return

    await state.update_data(phone=message.contact.phone_number)
    await RegisterFSM.passport.set()
    await message.answer("🛂 Passport JPG fayl yuboring (≤1MB):", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=RegisterFSM.passport)
async def passport(message: types.Message, state: FSMContext):
    doc = message.document

    if not doc.mime_type.startswith("image/") or doc.file_size > 1_000_000:
        await message.answer("❌ JPG rasm bo‘lishi va 1MB dan oshmasligi kerak")
        return

    data = await state.get_data()

    await db.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file)
        VALUES ($1,$2,$3,$4,$5)
        ON CONFLICT (telegram_id) DO NOTHING
    """,
        message.from_user.id,
        data["first_name"],
        data["last_name"],
        data["phone"],
        doc.file_id
    )

    await state.finish()

    await message.answer(
        "⏳ Maʼlumotlaringiz qabul qilindi.\n"
        "Admin tasdiqlashini kuting."
    )

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi foydalanuvchi:\n"
        f"{data['first_name']} {data['last_name']}\n"
        f"ID: {message.from_user.id}\n\n"
        f"/approve {message.from_user.id}\n"
        f"/reject {message.from_user.id}"
    )


# ================= ADMIN =================

@dp.message_handler(commands=["approve"])
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    user_id = int(message.get_args())

    await db.execute(
        "UPDATE users SET status='approved' WHERE telegram_id=$1",
        user_id
    )

    await bot.send_message(user_id, "✅ Tasdiqlandingiz. Botdan foydalanishingiz mumkin.")
    await message.answer("Tasdiqlandi ✅")


@dp.message_handler(commands=["reject"])
async def reject(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    user_id = int(message.get_args())

    await db.execute(
        "UPDATE users SET status='rejected' WHERE telegram_id=$1",
        user_id
    )

    await bot.send_message(user_id, "❌ Arizangiz rad etildi.")
    await message.answer("Rad etildi ❌")


@dp.message_handler(commands=["pending"])
async def pending(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    rows = await db.fetch("SELECT telegram_id, first_name FROM users WHERE status='pending'")
    if not rows:
        await message.answer("Pending yo‘q")
        return

    text = "⏳ Pending:\n"
    for r in rows:
        text += f"{r['first_name']} — {r['telegram_id']}\n"

    await message.answer(text)


# ================= RUN =================

async def on_startup(_):
    await init_db()
    print("✅ BOT ISHGA TUSHDI")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
