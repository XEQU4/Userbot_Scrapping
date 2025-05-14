import asyncio
import sys

from telethon import TelegramClient
from telethon import functions

from app.database.functions import get_chats_from_db, add_new_users_to_db_from_scrapping
from app.logger import logger


async def scrapping_chats(clients: list[TelegramClient]) -> None:
    chats = await get_chats_from_db()
    my_clients = [client[0] for client in clients]
    for chat in chats:
        try:
            async with my_clients[0] as client:
                receiver = await client.get_input_entity(chat['link'])
                all_participants = await client.get_participants(receiver)
            user_ids = [user.id for user in all_participants]
        except Exception as e:
            logger.error(f"[CHAT_ERROR] We cannot find the chat. Err: {e} | {chat}")
            continue

        for client in my_clients:
            async with client:
                if (await client.get_me()).id not in user_ids:
                    await client(functions.channels.JoinChannelRequest(
                        channel=chat['username']
                    ))

        users_to_db = []
        for user in all_participants:
            user_data = {
                "id": user.id,
                "username": user.username,
                "from_chat": chat['chat_id']
            }
            users_to_db.append(user_data)

        await add_new_users_to_db_from_scrapping(users_to_db)
