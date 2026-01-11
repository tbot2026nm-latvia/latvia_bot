import asyncio
from services.db import get_pool

async def monitor_loop():
    while True:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # hozircha test
            await conn.execute("SELECT 1")
        await asyncio.sleep(60)
