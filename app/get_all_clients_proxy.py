import os.path
import random

from app.database.functions import get_sessions_datas_from_db, get_proxies_datas_from_db, set_to_false_work_status, \
    set_last_timeout_proxy
from telethon import TelegramClient
import socks

from app.logger import logger


class GetClients:

    def __init__(self, proxy_on: bool = True):
        self.proxy = None
        self.proxy_on: bool = proxy_on
        self.proxy_dict: dict = None

    async def __next_proxy(self) -> bool:
        proxies_datas = await get_proxies_datas_from_db()
        if not proxies_datas:
            logger.error("[PROXY][NO PROXY] The number of proxies is less than one, although they are supposed to be used")
            return False

        if self.proxy is None:
            proxy_dict = proxies_datas[0]
        else:
            proxy_dict = None
            for index in range(len(proxies_datas)):
                if proxies_datas[index] == self.proxy_dict:
                    try:
                        proxy_dict = proxies_datas[index + 1]
                    except:
                        proxy_dict = proxies_datas[0]
                    break

        if proxy_dict['proxy_type'] == 'socks5':
            self.proxy = (socks.SOCKS5, proxy_dict['addr'], proxy_dict['port'], True, proxy_dict['username'], proxy_dict['password'])
        elif proxy_dict['proxy_type'] == 'socks4':
            self.proxy = (socks.SOCKS4, proxy_dict['addr'], proxy_dict['port'], True, proxy_dict['username'], proxy_dict['password'])
        elif proxy_dict['proxy_type'] == 'http':
            self.proxy = (socks.HTTP, proxy_dict['addr'], proxy_dict['port'], True, proxy_dict['username'], proxy_dict['password'])
        else:
            logger.error(f"[PROXY][ERROR_TYPE] The proxy type must be one of 'socks5', 'socks4', or 'http' - {proxy_dict}")
        self.proxy_dict = proxy_dict
        return True

    async def __create_client(self, session_data: dict) -> TelegramClient | None:
        path = os.path.abspath("") + "\\sessions\\sessions\\"

        device_models = [
            "Samsung Galaxy S23",
            "iPhone 15 Pro",
            "Google Pixel 8",
            "Xiaomi 13 Pro",
            "OnePlus 11"
        ]
        system_versions = [
            "Android 14",
            "iOS 17",
            "Android 13",
            "iOS 16.5"
        ]
        app_versions = [
            "Telegram Android 10.2.1",
            "Telegram iOS 9.6",
            "Telegram Android 11.0.0",
            "Telegram iOS 10.1.0"
        ]
        lang_codes = ["ru", "en", "uk", "de"]
        system_lang_codes = ["ru-RU", "en-US", "uk-UA", "de-DE"]

        # Рандомные метаданные
        device_model = random.choice(device_models)
        system_version = random.choice(system_versions)
        app_version = random.choice(app_versions)
        lang_code = random.choice(lang_codes)
        system_lang_code = random.choice(system_lang_codes)

        try:
            if self.proxy_on:
                client = TelegramClient(path + session_data['session_name'],
                                        api_id=session_data['api_id'],
                                        api_hash=session_data['api_hash'],
                                        proxy=self.proxy,
                                        timeout=60,
                                        request_retries=3,
                                        connection_retries=1,
                                        device_model=device_model,
                                        system_version=system_version,
                                        app_version=app_version,
                                        lang_code=lang_code,
                                        system_lang_code=system_lang_code)
            else:
                client = TelegramClient(path + session_data['session_name'],
                                        api_id=session_data['api_id'],
                                        api_hash=session_data['api_hash'],
                                        timeout=60,
                                        request_retries=3,
                                        connection_retries=1,
                                        device_model=device_model,
                                        system_version=system_version,
                                        app_version=app_version,
                                        lang_code=lang_code,
                                        system_lang_code=system_lang_code)

            await client.connect()
            if not await client.is_user_authorized():
                logger.warning(f"[SESSION][NOT_AUTHORIZED][WORK_STATUS_FALSE] Session is not authorized - {session_data}")
                await set_to_false_work_status(session_data['session_name'])
                await client.disconnect()
                return None
            await client.disconnect()
            return client
        except ConnectionError:
            logger.error(f"[PROXY][CONNECTION_ERROR][TRY_WITH_NEXT_PROXY] Session is not working with this proxy. {self.proxy_dict} | {session_data}")
            await set_last_timeout_proxy(self.proxy_dict)
            await self.__next_proxy()
            client = await self.__create_client(session_data)
            return client
        except Exception as e:
            logger.exception(f"[SESSION][ERROR][WORK_STATUS_FALSE] Session is not working. Err: {e} | {session_data}")
            await set_to_false_work_status(session_data['session_name'])
            return None

    async def get_all_clients(self) -> list[list[TelegramClient, str]] | None:
        sessions_datas = await get_sessions_datas_from_db(work_status_only_true=True)
        clients: list[(TelegramClient, str)] = []
        for session_data in sessions_datas:
            if self.proxy_on:
                while True:
                    flag = await self.__next_proxy()
                    if not flag:
                        return None
                    if self.proxy is not None:
                        break

            client = await self.__create_client(session_data)
            if client is not None:
                clients.append([client, session_data['session_name']])
                logger.info(f"[SESSION] Session is ready to work - {session_data}")

        if not clients:
            logger.error("[SESSION][NO SESSION] The number of sessions is less than one")
            return None
        return clients
