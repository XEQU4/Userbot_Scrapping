import json
import os
from datetime import datetime
import pytz

from app.database.pool import db
from app.logger import logger


@logger.catch
async def add_new_sessions_from_json() -> None:
    path = os.path.abspath("") + "\\"
    with open(f"{path}sessions\\new_sessions.json", encoding="utf-8") as file:
        data: dict = json.load(file)
    new_sessions_names_list = [key for key, val in data.items()]
    if not new_sessions_names_list:
        return

    accounts = await get_sessions_datas_from_db()
    sessions_names_list = [account['session_name'] for account in accounts]

    pool = await db.get_pool()

    for session_name in new_sessions_names_list:
        session_data = data[session_name]

        if session_name in sessions_names_list:
            query = """
            UPDATE accounts 
            SET api_id = $1, api_hash = $2, phone_number = $3, password = $4, work_status = true
            WHERE session_name = $5
            """

            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(query,
                                       session_data['api_id'],
                                       session_data['api_hash'],
                                       session_data['phone'],
                                       session_data['password'],
                                       session_name)

            logger.info(f"[DATABASE][UPDATE] Session data updated - \"{session_data}\"")

            del data[session_name]
            with open(f"{path}sessions\\new_sessions.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        else:
            query = """
            INSERT INTO accounts 
            VALUES ($1, $2, $3, $4, $5, true)
            """

            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(query,
                                       session_name,
                                       session_data['api_id'],
                                       session_data['api_hash'],
                                       session_data['phone'],
                                       session_data['password'])

            logger.info(f"[DATABASE][INSERT] New session added - \"{session_data}\"")

            del data[session_name]
            with open(f"{path}sessions\\new_sessions.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)


@logger.catch
async def add_new_proxies_from_txt() -> None:
    path = os.path.abspath("") + "\\"
    with open(f"{path}sessions\\proxies_datas.txt", encoding="utf-8") as file:
        txt_data = [proxy_str.rstrip('\n') for proxy_str in file.readlines()[1:] if proxy_str.rstrip('\n')]
    if not txt_data:
        return

    proxies_from_txt = []
    for proxy_string in txt_data:
        proxy_data_list = proxy_string.split(":")
        proxies_from_txt.append(
            {
                "proxy_type": proxy_data_list[0],
                "addr": proxy_data_list[1],
                "port": int(proxy_data_list[2]),
                "username": proxy_data_list[3],
                "password": proxy_data_list[4],
            }
        )
    proxies_from_db = [{key: val for key, val in proxy_data.items() if key != 'last_timeout'}
                       for proxy_data in await get_proxies_datas_from_db()]
    # proxies_from_txt / proxies_from_db: {"proxy_type": "http", "addr": "192.168.1.100", "port": 8080, "username": "user123", "password": "pass123"}

    for proxy_data in proxies_from_txt:
        if proxy_data not in proxies_from_db:
            query = """
            INSERT INTO proxies
            VALUES ($1, $2, $3, $4, $5)
            """

            pool = await db.get_pool()

            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(query,
                                       proxy_data['proxy_type'],
                                       proxy_data['addr'],
                                       proxy_data['port'],
                                       proxy_data['username'],
                                       proxy_data['password'])

            logger.info(f"[DATABASE][INSERT] New proxy added - \"{proxy_data}\"")


@logger.catch
async def get_sessions_datas_from_db(work_status_only_true: bool = False) -> list[dict]:
    """
    [\n
    {'session_name': 'name1', 'api_id': 12345, 'api_hash': 'abc123hash', 'phone_number': '+77070000000', 'work_status': True},\n
    {'session_name': 'name2', 'api_id': 67890, 'api_hash': 'def456hash', 'phone_number': '+77079999999', 'work_status': False},\n
    {'session_name': 'name3', 'api_id': 54321, 'api_hash': 'ghi789hash', 'phone_number': '+77078888888', 'work_status': True},\n
    {'session_name': 'name3', 'api_id': 98765, 'api_hash': 'jkl012hash', 'phone_number': '+77077777777', 'work_status': False},\n
    . . .\n
    ]
    """
    if not work_status_only_true:
        query = """
        SELECT * FROM accounts
        """
    else:
        query = """
        SELECT * FROM accounts WHERE work_status IS DISTINCT FROM false
        """

    pool = await db.get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            records = await conn.fetch(query)

    accounts = [dict(account_record) for account_record in records]

    return accounts


@logger.catch
async def set_to_false_work_status(session_name: str) -> None:
    """Меняет статус рабочей сессии на нерабочий"""
    accounts = await get_sessions_datas_from_db()
    sessions_names_list = [account['session_name'] for account in accounts]

    if session_name in sessions_names_list:
        query = """
        UPDATE accounts
        SET work_status = false
        WHERE session_name = $1
        """

        pool = await db.get_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query,
                                   session_name)

        logger.warning(f"[DATABASE][UPDATE] The session work_status has been set to false - \"{session_name}\"")


@logger.catch
async def get_proxies_datas_from_db() -> list[dict]:
    """
    [\n
        {"proxy_type": "http", "addr": "192.168.1.100", "port": 8080, "username": "user123", "password": "pass123", "last_timeout": "0"}\n
        {"proxy_type": "socks5", "addr": "10.0.0.55", "port": 1080, "username": "proxyuser", "password": "securepass", "last_timeout": "2025-04-20 12:35:10"}\n
        {"proxy_type": "http", "addr": "203.0.113.12", "port": 3128, "username": "", "password": "", "last_timeout": "0"}\n
    . . .\n
    ]
    """
    query = """
    SELECT * FROM proxies
    """

    pool = await db.get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            records = await conn.fetch(query)

    proxies = [dict(proxy_record) for proxy_record in records]

    return proxies


@logger.catch
async def set_last_timeout_proxy(proxy: dict) -> None:
    """Меняет последнее время не срабатывания на текущий

    :param proxy: {'proxy_type': 'socks5', 'addr': '1.1.1.1', 'port': 5555, 'username': 'foo', 'password': 'bar', 'last_timeout': '2025-04-12 15:12:32'}
    """
    proxies = await get_proxies_datas_from_db()

    if proxy in proxies:
        moscow_tz = pytz.timezone("Europe/Moscow")
        dt = datetime.now(tz=moscow_tz)

        query = """
        UPDATE proxies
        SET last_timeout = $1
        WHERE proxy_type = $2 AND addr = $3 AND port = $4 AND username = $5 AND password = $6
        """

        pool = await db.get_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query,
                                   dt,
                                   proxy["proxy_type"],
                                   proxy["addr"],
                                   proxy["port"],
                                   proxy["username"],
                                   proxy["password"],)

        logger.warning(f"[DATABASE][UPDATE] The last proxy timeout has changed, but it will still be used next time - \"{proxy}\" to \"{dt}\"")


@logger.catch
async def get_chats_from_db() -> list[str]:
    """
    [\n
        {'chat_id': -1001234567890, 'username': 'cybersecurity_group', 'link': 'https://t.me/cybersecurity_group'},\n
        {'chat_id': -1009876543210, 'username': 'dev_news', 'link': 'https://t.me/dev_news'},\n
        {'chat_id': -1001122334455, 'username': 'daily_ai', 'link': 'https://t.me/daily_ai'},\n
        {'chat_id': -1006677889900, 'username': 'python_world', 'link': 'https://t.me/python_world'},\n
        {'chat_id': -1005566778899, 'username': 'tech_feed', 'link': 'https://t.me/tech_feed'}\n
    ]
    """
    query = """
    SELECT * FROM chats
    """

    pool = await db.get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            records = await conn.fetch(query)

    chats = [dict(chat_record) for chat_record in records]

    return chats


@logger.catch
async def get_users_from_db(spam_status_only_false_reason_null: bool = False) -> list[dict]:
    """
    [\n
        {'id': 1, 'username': 'john_doe', 'from_chat': 1001234567, 'spam_status': 0, 'spam_time': None, 'spam_error_reason': None},\n
        {'id': 2, 'username': 'jane_smith', 'from_chat': 1009876543, 'spam_status': 1, 'spam_time': '2025-04-21 12:30:00', 'spam_error_reason': 'FloodWaitError'},\n
        {'id': 3, 'username': 'bot_checker', 'from_chat': 1001122334, 'spam_status': 0, 'spam_time': None, 'spam_error_reason': None}]\n
        . . .\n
    ]\n
    if spam_status_only_false_reason_null = True:\n
    [\n
        {'id': 1, 'username': 'john_doe', 'from_chat': 1001234567, 'spam_status': 0, 'spam_time': None, 'spam_error_reason': None},\n
        {'id': 3, 'username': 'bot_checker', 'from_chat': 1001122334, 'spam_status': 0, 'spam_time': None, 'spam_error_reason': None}]\n
        . . .\n
    ]
    """
    if spam_status_only_false_reason_null:
        query = """
        SELECT * FROM users WHERE spam_status = false AND spam_error_reason IS NULL
        """
    else:
        query = """
        SELECT * FROM users
        """

    pool = await db.get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            records = await conn.fetch(query)

    users = [dict(chat_record) for chat_record in records]

    return users


@logger.catch
async def add_new_users_to_db_from_scrapping(users: list[dict]) -> None:
    """
    :param users: [{"id": 789456123, "username": "hello_world", "from_chat": 1001234567}, . . .]
    """
    users_from_db = await get_users_from_db()
    users_ids_from_db = [[val for key, val in user.items() if key == "id"][0] for user in users_from_db]  # Получаем список id пользователей из юазы данных

    pool = await db.get_pool()
    count = 0

    for user in users:
        if user['id'] not in users_ids_from_db:
            if user['username'] is not None:
                query = """
                INSERT INTO users (id, username, from_chat)
                VALUES ($1, $2, $3)
                """
                async with pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(query,
                                           user['id'],
                                           user['username'],
                                           user['from_chat'])
            else:
                query = """
                INSERT INTO users (id, from_chat, spam_error_reason)
                VALUES ($1, $2, $3)
                """
                async with pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(query,
                                           user['id'],
                                           user['from_chat'],
                                           "USERNAME_NOT_FOUND - The user does not have a username, so spam will not be sent to them")

            count += 1

    logger.info(f"[DATABASE][INSERT] New users added - \"{count}\"")


@logger.catch
async def set_user_spam_status_to_true_and_time(user_id: int, spam_time: datetime) -> None:
    query = """
    UPDATE users
    SET spam_status = true, spam_time = $1
    WHERE id = $2
    """

    pool = await db.get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(query,
                               spam_time,
                               user_id)


@logger.catch
async def set_user_reason_and_time(user_id: int, spam_time: datetime, reason: str) -> None:
    query = """
    UPDATE users
    SET spam_error_reason = $1, spam_time = $2
    WHERE id = $3
    """

    pool = await db.get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(query,
                               reason,
                               spam_time,
                               user_id)

    logger.warning(f"[DATABASE][UPDATE] Failed to send message to this user; reason and timestamp have been recorded in the database - {user_id} - {reason}")
