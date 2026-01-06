import os
import asyncio
import hashlib
import aiohttp
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL_TO_MONITOR = os.getenv("URL_TO_MONITOR")
CHECK_INTERVAL = 60

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =====================
# DATA (hozircha xotirada)
# =====================

users = {}        # chat_id -> {name, phone}
subscribers = set()
_last_hash = None
_initialized = False
waiting_for_name = set()
waiting_for_phone = set()

# =====================
# START
# =====================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    chat_id = message.chat.id

    if chat_id in users:
        await message.answer(
            "Siz allaqachon ro‘yxatdan o‘tgansiz ✅\n\n"
            "/subscribe — kuzatuvga qo‘shilish\n"
            "/unsubscribe — chiqish"
        )
        return

    waiting_for_name.add(chat_id)
    await message.answer("Iltimos, ism va familiyangizni kiriting:")

# =====================
# NAME INPUT
# =====================

@dp.message_handler(lambda m: m.chat.id in waiting_for_name, content_types=types.ContentTypes.TEXT)
async def get_name(message: types.Message):
    chat_id = message.chat.id
    name = message.text.strip()

    users[chat_id] = {"name": name}
    waiting_for_name.remove(chat_id)
    waiting_for_phone.add(chat_id)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))

    await message.answer(
        f"Rahmat, {name}.\nEndi telefon raqamingizni yuboring:",
        reply_markup=kb
    )

# =====================
# PHONE INPUT
# =====================

@dp.message_handler(lambda m: m.chat.id in waiting_for_phone, content_types=types.ContentTypes.CONTACT)
async def get_phone(message: types.Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number

    users[chat_id]["phone"] = phone
    waiting_for_phone.remove(chat_id)

    await message.answer(
        "✅ Ro‘yxatdan muvaffaqiyatli o‘tdingiz!\n\n"
        "/subscribe — kuzatuvga qo‘shilish",
        reply_markup=types.ReplyKeyboardRemove()
    )

# =====================
# SUBSCRIBE
# =====================

@dp.message_handler(commands=["subscribe"])
async def subscribe(message: types.Message):
    chat_id = message.chat.id

    if chat_id not in users:
        await message.answer("❌ Avval ro‘yxatdan o‘ting: /start")
        return

    subscribers.add(chat_id)
    await message.answer("Siz kuzatuvga qo‘shildingiz ✅")

@dp.message_handler(commands=["unsubscribe"])
async def unsubscribe(message: types.Message):
    subscribers.discard(message.chat.id)
    await message.answer("Siz kuzatuvdan chiqdingiz ❌")

# =====================
# MONITOR
# =====================

async def monitor():
    global _last_hash, _initialized

    if not URL_TO_MONITOR:
        return

    print(f"👀 Monitoring boshlandi: {URL_TO_MONITOR}")

    async with aiohttp.ClientSession() as session:
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                async with session.get(URL_TO_MONITOR, timeout=20) as resp:
                    text = await resp.text()
                    status = resp.status

                current_hash = hashlib.md5(text.encode()).hexdigest()

                if not _initialized:
                    _last_hash = current_hash
                    _initialized = True
                else:
                    if current_hash != _last_hash:
                        for user_id in subscribers:
                            await bot.send_message(
                                user_id,
                                f"⚠️ Saytda o‘zgarish aniqlandi!\n"
                                f"📡 Status: {status}\n"
                                f"⏰ Vaqt: {now}"
                            )
                        _last_hash = current_hash

            except Exception as e:
                for user_id in subscribers:
                    await bot.send_message(
                        user_id,
                        f"❌ Monitoring xatosi\n⏰ {now}\n{e}"
                    )

            await asyncio.sleep(CHECK_INTERVAL)

# =====================
# STARTUP
# =====================

async def on_startup(dp):
    print("✅ BOT ISHGA TUSHDI")
    asyncio.create_task(monitor())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)