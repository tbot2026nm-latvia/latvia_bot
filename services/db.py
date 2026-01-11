import asyncpg
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL")

pool: asyncpg.Pool | None = None


# ========================
# CONNECT
# ========================
async def connect_db():
    global pool
    if pool:
        return pool

    pool = await asyncpg.create_pool(DATABASE_URL, ssl="require")

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            passport_file TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)

    logging.info("✅ Database ulandi")
    return pool


# ========================
# CREATE USER
# ========================
async def create_user(telegram_id: int, first_name: str, last_name: str, phone: str, passport_file: str):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file, status)
        VALUES ($1, $2, $3, $4, $5, 'pending')
        ON CONFLICT (telegram_id) DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            phone = EXCLUDED.phone,
            passport_file = EXCLUDED.passport_file,
            status = 'pending'
        """, telegram_id, first_name, last_name, phone, passport_file)


# ========================
# UPDATE STATUS
# ========================
async def update_user_status(telegram_id: int, status: str):
    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE users SET status=$1 WHERE telegram_id=$2
        """, status, telegram_id)


# ========================
# GET USER
# ========================
async def get_user(telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
        SELECT * FROM users WHERE telegram_id=$1
        """, telegram_id)


# ========================
# IS USER APPROVED
# ========================
async def is_user_approved(telegram_id: int) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT status FROM users WHERE telegram_id=$1
        """, telegram_id)

        if not row:
            return False

        return row["status"] == "approved"
