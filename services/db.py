import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None


async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            passport TEXT,
            status TEXT DEFAULT 'pending'
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            service TEXT,
            location TEXT,
            status TEXT DEFAULT 'waiting',
            last_check TIMESTAMP,
            found BOOLEAN DEFAULT FALSE
        );
        """)


# ================= USERS =================

async def create_user(telegram_id, first_name, last_name, phone, passport_file):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport)
        VALUES ($1,$2,$3,$4,$5)
        ON CONFLICT (telegram_id) DO NOTHING
        """, telegram_id, first_name, last_name, phone, passport_file)


async def update_user_status(telegram_id, status):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET status=$1 WHERE telegram_id=$2", status, telegram_id)


async def get_user(telegram_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE telegram_id=$1", telegram_id)


# ================= QUEUE =================

async def add_queue(user_id, service, location):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO queue (user_id, service, location)
        VALUES ($1,$2,$3)
        """, user_id, service, location)


async def get_user_queue(user_id):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM queue WHERE user_id=$1")


async def set_queue_found(queue_id):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE queue SET found=TRUE, status='found' WHERE id=$1", queue_id)

# ===== ADMIN =====

async def get_pending_users():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users WHERE status='pending'")
