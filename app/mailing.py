import asyncio
import os.path
import random
import datetime

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, PeerFloodError, ChatWriteForbiddenError,
    UsernameNotOccupiedError, UserIsBlockedError,
    InputUserDeactivatedError, MessageTooLongError,
    MediaCaptionTooLongError, RPCError
)

from app.get_all_clients_proxy import GetClients
from app.scrapping import scrapping_chats
from app.database.functions import add_new_sessions_from_json, get_users_from_db, add_new_proxies_from_txt, \
    set_user_spam_status_to_true_and_time, set_user_reason_and_time, set_to_false_work_status
from app.logger import logger


async def main_function_mailing():
    count = 0
    while True:
        await add_new_sessions_from_json()
        await add_new_proxies_from_txt()

        clients_class = GetClients()
        clients = await clients_class.get_all_clients()
        await scrapping_chats(clients)

        users = await get_users_from_db(spam_status_only_false_reason_null=True)
        if users is None:
            logger.warning("[USERS][NO USERS] The number of users for the mailing is less than one")
            continue
        start_index, end_index = 0, len(users) // len(clients)  # Интервал юзернеймов для разделения между клиентами
        interval = end_index

        results: list[dict]  # [{
        #     "session_name": None  # str: name of the session
        #     "user_data": None,  # str: datas of the user
        #     "status": None,  # bool: spam status
        #     "error_type": None,  # str: the type of error: client | user
        #     "error_reason": None,  # str: the reason of error
        #     "timestamp": None,  # datetime: the time of mailing
        # }, ...]

        path = os.path.abspath("")
        with open(f"{path}\\our_message\\message_text.txt", encoding="utf-8") as f:
            text = f.read()
            image_path = None
        if len(os.listdir(f"{path}\\our_message")) == 2:
            for file in os.listdir(f"{path}\\our_message"):
                if file != 'message_text.txt':
                    image_path = f"{path}\\our_message\\{file}"
                    break

        print()
        logger.info("[MAILING] Starting the mailing . . .")
        print()
        if end_index != 0 and len(users) % len(clients) == 0:
            tasks = []
            for client in clients:
                client_users = users[start_index: end_index]
                start_index = end_index
                end_index = end_index + interval

                tasks.append(mailing(client[0], client_users, client[1], text, image_path))

            all_results: list[list[int]] = await asyncio.gather(*tasks)
        else:  # Если количество сессий больше чем пользователей, то спамим только с первого аккаунта
            all_results: list[list[int]] = list(await mailing(clients[0][0], users, clients[0][1], text, image_path))
        print()

        results_status_true = 0
        results_users = 0
        results_clients = 0
        for results_list in all_results:
            results_status_true += results_list[0]
            results_users += results_list[1]
            results_clients += results_list[2]

        logger.info("[MAILING] End of mailing. Statistics: \n"
                    f"      Successful mailings: {results_status_true}\n"
                    f"      Unsuccessful due to users: {results_users}\n"
                    f"      Unsuccessful due to sessions: {results_clients}")
        print()

        count += 1
        if count % 5 == 0 and count != 0:
            sleep_time = random.randint(12 * 60 * 60, 24 * 60 * 60)
            sleep_time_text = (sleep_time / 60 / 60) + " hours"
        else:
            sleep_time = random.randint(45 * 60, 75 * 60)
            sleep_time_text = (sleep_time / 60) + " minutes"
        logger.info(f"[MAILING] Going to sleep - {sleep_time_text}")
        await asyncio.sleep(sleep_time)


async def mailing(client: TelegramClient, users: list[dict], session_name: str, text: str, image_path: str = None) -> list[dict]:
    results = [0, 0, 0]

    try:
        async with client:
            if not await client.is_user_authorized():
                logger.error(f"[MAILING][ERR_TYPE_SESSION][NOT_AUTHORIZED] Session is not authorized: {session_name}")
                results[2] += 1
                await set_to_false_work_status(session_name)
                return results

            for user in users:
                await asyncio.sleep(random.randint(5, 10))
                username = user.get("username")
                try:
                    entity = await client.get_entity(username)

                    if image_path:
                        await client.send_file(
                            entity=entity,
                            file=image_path,
                            caption=text,
                            parse_mode="markdown"
                        )
                    else:
                        await client.send_message(
                            entity=entity,
                            message=text,
                            parse_mode="markdown"
                        )

                    logger.debug(f"[MAILING][SUCCESSFUL] Session: {session_name} - User: {user}")
                    results[0] += 1
                    await set_user_spam_status_to_true_and_time(user_id=user['id'], spam_time=datetime.datetime.now())

                except (UsernameNotOccupiedError, InputUserDeactivatedError, ChatWriteForbiddenError,
                        UserIsBlockedError, PeerFloodError, MessageTooLongError, MediaCaptionTooLongError) as e:
                    logger.warning(f"[MAILING][ERR_TYPE_USER] Session: {session_name} - The mailing to this user failed: {user} | Err: {str(e)}")
                    results[1] += 1
                    await set_user_reason_and_time(user['id'], datetime.datetime.now(), str(e))

                except FloodWaitError as e:
                    logger.warning(f"[MAILING][SESSION][FLOOD_WAIT] Session: {session_name} - Wait for {e.seconds} seconds. Session "
                                   f"has stopped this mailing cycle. The users who didn't receive the message this time will be targeted in future attempts")
                    break

                except RPCError as e:
                    logger.error(f"[MAILING][ERR_TYPE_USER][RPC_ERROR] Session: {session_name} - The mailing to this user failed: {user} | Err: {str(e)}")
                    results[1] += 1
                    await set_user_reason_and_time(user['id'], datetime.datetime.now(), str(e))

                except Exception as e:
                    logger.exception(f"[MAILING][ERR_TYPE_USER][UNEXPECTED ERROR] Session: {session_name} - The mailing to this user failed: {user} | Err: {str(e)}")
                    results[1] += 1
                    await set_user_reason_and_time(user['id'], datetime.datetime.now(), str(e))

    except Exception as e:
        logger.exception(f"[MAILING][ERR_TYPE_SESSION][FATAL_ERROR] The session stopped responding: {session_name} | Err: {str(e)}")
        results[2] += 1
        await set_to_false_work_status(session_name)

    return results
