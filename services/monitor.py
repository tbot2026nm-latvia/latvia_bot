import asyncio
import random
from services.db import pool
from datetime import datetime

async def monitor_loop(bot):
    while True:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM queue WHERE found=FALSE")
            for r in rows:
                if random.random() > 0.95:  # 5% chance found
                    await conn.execute(
                        "UPDATE queue SET found=TRUE, status='FOUND', last_checked=NOW() WHERE id=$1",
                        r["id"]
                    )
                    await bot.send_message(
                        r["user_id"],
                        f"🎉 SLOT TOPILDI!\n{r['service']} / {r['location']}"
                    )
        await asyncio.sleep(30)
