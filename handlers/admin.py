from aiogram import Router, types
from services.db import set_status

router = Router()

@router.callback_query(lambda c: c.data.startswith("ok_"))
async def approve(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    await set_status(uid, "approved")
    await call.bot.send_message(uid, "✅ Tasdiqlandingiz!")
    await call.answer("Tasdiqlandi")

@router.callback_query(lambda c: c.data.startswith("no_"))
async def reject(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    await set_status(uid, "rejected")
    await call.bot.send_message(uid, "❌ Rad etildi")
    await call.answer("Rad etildi")
