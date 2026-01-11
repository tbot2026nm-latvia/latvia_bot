import asyncpg
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")
pool = None


async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

    await pool.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id BIGINT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        passport_file TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    await pool.execute("""
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


# ---------- USERS ----------

async def create_user(telegram_id, first_name, last_name, phone, passport_file):
    await pool.execute("""
        INSERT INTO users (telegram_id, first_name, last_name, phone, passport_file)
        VALUES ($1,$2,$3,$4,$5)
        ON CONFLICT (telegram_id) DO NOTHING
    """, telegram_id, first_name, last_name, phone, passport_file)


async def update_user_status(telegram_id, status):
    await pool.execute(
        "UPDATE users SET status=$1 WHERE telegram_id=$2",
        status, telegram_id
    )


async def get_user(telegram_id):
    return await pool.fetchrow(
        "SELECT * FROM users WHERE telegram_id=$1", telegram_id
    )


async def get_pending_users():
    return await pool.fetch("SELECT * FROM users WHERE status='pending'")

# ============================
# QUEUE FUNCTIONS
# ============================

async def add_queue(user_id: int, service: str, location: str):
    await pool.execute("""
        INSERT INTO queue (user_id, service, location, status, last_check, found)
        VALUES ($1, $2, $3, 'waiting', NOW(), FALSE)
    """, user_id, service, location)


async def get_user_queue(user_id: int):
    return await pool.fetch("""
        SELECT * FROM queue
        WHERE user_id=$1
        ORDER BY id DESC
    """, user_id)


async def mark_queue_found(queue_id: int):
    await pool.execute("""
        UPDATE queue
        SET found=TRUE, status='found'
        WHERE id=$1
    """, queue_id)


async def update_last_check(queue_id: int):
    await pool.execute("""
        UPDATE queue
        SET last_check=NOW()
        WHERE id=$1
    """, queue_id)


async def get_active_queues():
    return await pool.fetch("""
        SELECT * FROM queue
        WHERE found=FALSE
    """)
