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
                joined_at TIMESTAMP DEFAULT NOW()
            )
        """)

async def save_user(pool, user_id: int, username: str, full_name: str):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id, username, full_name)

async def get_all_users(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT user_id FROM users")
