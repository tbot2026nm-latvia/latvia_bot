import aiohttp
import asyncio
from services.db import pool

VFS_URL = "https://visa.vfsglobal.com/uz/ru/lva/"


async def check_vfs():
    async with aiohttp.ClientSession() as session:
        async with session.get(VFS_URL) as r:
            return r.status == 200


async def monitor_loop(bot):
    while True:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM queue WHERE found=FALSE")

            for row in rows:
                ok = await check_vfs()
                if ok:
                    await conn.execute(
                        "UPDATE queue SET found=TRUE WHERE id=$1", row["id"]
                    )
                    await bot.send_message(
                        row["user_id"],
                        "🎉 Latvia uchun navbat OCHILDI!"
                    )

        await asyncio.sleep(60)
