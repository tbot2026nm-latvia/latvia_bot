import asyncpg
import os
import logging

pool = None

async def connect_db():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
        logging.info("✅ Database ulandi")

async def get_pool():
    if pool is None:
        raise RuntimeError("DB pool hali yaratilmagan")
    return pool
