import asyncpg
import os

async def get_pool():
    return await asyncpg.create_pool(os.environ["DATABASE_URL"])

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT NOW(),
                in_progress BOOLEAN DEFAULT FALSE
            )
        """)
        try:
            await conn.execute("""
                ALTER TABLE users ADD COLUMN IF NOT EXISTS in_progress BOOLEAN DEFAULT FALSE
            """)
        except Exception:
            pass

async def save_user(pool, user_id: int, username: str, full_name: str):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id, username, full_name)

async def set_in_progress(pool, user_id: int, value: bool):
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users SET in_progress = $1 WHERE user_id = $2
        """, value, user_id)

async def is_in_progress(pool, user_id: int) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT in_progress FROM users WHERE user_id = $1", user_id
        )
        return row["in_progress"] if row else False

async def get_all_users(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT user_id FROM users")
