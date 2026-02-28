import os
import asyncpg
import logging

logger = logging.getLogger(__name__)

pool = None

async def init_db():
    global pool
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.warning("No DATABASE_URL found in environment. DB features will be disabled.")
        return
    try:
        pool = await asyncpg.create_pool(database_url)
        logger.info("Database pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")

async def close_db():
    global pool
    if pool:
        await pool.close()
        logger.info("Database pool closed")

async def create_session() -> int | None:
    if not pool:
        return None
    try:
        async with pool.acquire() as conn:
            session_id = await conn.fetchval(
                "INSERT INTO sessions DEFAULT VALUES RETURNING id;"
            )
            return session_id
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return None

async def end_session(session_id: int):
    if not pool or not session_id:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE sessions SET ended_at = NOW() WHERE id = $1",
                session_id
            )
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {e}")

async def set_session_summary(session_id: int, summary: str):
    if not pool or not session_id:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE sessions SET summary = $1 WHERE id = $2",
                summary, session_id
            )
    except Exception as e:
        logger.error(f"Error setting session summary for {session_id}: {e}")

async def add_message(session_id: int, role: str, content: str):
    if not pool or not session_id:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES ($1, $2, $3)",
                session_id, role, content
            )
    except Exception as e:
        logger.error(f"Error adding message to session {session_id}: {e}")

async def get_last_session_summary() -> str:
    if not pool:
        return ""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT summary FROM sessions WHERE summary IS NOT NULL ORDER BY id DESC LIMIT 1"
            )
            return row['summary'] if row else ""
    except Exception as e:
        logger.error(f"Error fetching last session summary: {e}")
        return ""

async def get_pinned_memories() -> list[dict]:
    if not pool:
        return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT content, category FROM pinned_memories ORDER BY pinned_at ASC"
            )
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Error fetching pinned memories: {e}")
        return []

async def get_messages_for_session(session_id: int) -> list[dict]:
    if not pool or not session_id:
        return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT role, content FROM messages WHERE session_id = $1 ORDER BY id ASC",
                session_id
            )
            return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception as e:
        logger.error(f"Error fetching messages for session {session_id}: {e}")
        return []
