import sys

from app.database.pool import db
from app.logger import logger
from asyncpg import exceptions


@logger.catch
async def create_tables() -> None:
    """
    Creating tables in the database
    """

    pool = await db.get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.transaction():
                query = """
                        CREATE TABLE IF NOT EXISTS accounts (
                            session_name TEXT PRIMARY KEY,
                            api_id INTEGER,
                            api_hash TEXT,
                            phone_number TEXT,
                            password TEXT,
                            work_status BOOLEAN DEFAULT true
                        )
                        """
                await conn.execute(query)

                query = """
                        CREATE TABLE IF NOT EXISTS proxies (
                            proxy_type VARCHAR(10),
                            addr VARCHAR(25),
                            port INTEGER,
                            username TEXT,
                            password TEXT,
                            last_timeout TIMESTAMP DEFAULT null
                        )
                        """
                await conn.execute(query)

                query = """
                        CREATE TABLE IF NOT EXISTS chats (
                            chat_id BIGINT PRIMARY KEY,
                            username TEXT,
                            link TEXT
                        )
                        """
                await conn.execute(query)

                query = """
                        CREATE TABLE IF NOT EXISTS users (
                            id BIGINT PRIMARY KEY,
                            username TEXT DEFAULT null,
                            from_chat BIGINT,
                            spam_status BOOLEAN DEFAULT false,
                            spam_time TIMESTAMP DEFAULT null,
                            spam_error_reason TEXT DEFAULT null
                        )
                        """
                await conn.execute(query)

        except exceptions.PostgresError as err:
            logger.error(f"[DATABASE][TABLES] TABLES ARE NOT CREATED, SO THE BOT IS STOPPED! ERROR - {err}")
            sys.exit()

        else:
            logger.info("[DATABASE][TABLES] ALL TABLES HAVE BEEN CREATED IN THE DATABASE!")
