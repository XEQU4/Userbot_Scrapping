import asyncio
import contextlib
import json
import os
import random
import socks

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from app.database.functions import get_proxies_datas_from_db
from app.database.pool import db


path = os.path.abspath("")
sessions_names_list = [session_name_fl.rstrip(".session") for session_name_fl in os.listdir(f"{path}\\sessions")]

with open(f"{path}\\sessions_datas.txt") as f:
    accounts_list = f.readlines()[1:]
    accounts: list[dict] = []

    for account_string in accounts_list:
        account_list = account_string.strip().split("/")

        accounts.append({
            "session_name": account_list[0],
            "api_id": int(account_list[1]),
            "api_hash": account_list[2],
            "password": account_list[3],
            "phone": account_list[4],
        })

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


async def login_account(account, proxy):
    await asyncio.sleep(random.uniform(0.5, 1.5))
    session_name = account['session_name']
    session_path = f"{path}\\sessions\\{session_name}.session"
    api_id = account['api_id']
    api_hash = account['api_hash']
    phone = account['phone']
    password = account['password']
    print(f"[{session_name}] Проверка авторизации. Сессия: {account}")

    if session_name in sessions_names_list:
        while True:
            response = input(f"[{session_name}] Сессия с таким именем уже существует. Подтверждаете его замену на новый? Данные изменятся и в базе данных при следующем парсинге чатов [1, 0]: ")

            if response == '1':
                try:
                    os.remove(f"{path}\\sessions\\{session_name}.session")
                except BaseException as err:
                    print(f"[{session_name}] При удалений произошла ошибка: {err} ⛔️. Переходим к следующим данным\n")
                    return
                break
            elif response == '0':
                print(f"[{session_name}] Отмена создания данной сессий ⛔️\n")
                return

    # Рандомные метаданные
    device_model = random.choice(device_models)
    system_version = random.choice(system_versions)
    app_version = random.choice(app_versions)
    lang_code = random.choice(lang_codes)
    system_lang_code = random.choice(system_lang_codes)

    client = TelegramClient(session_path,
                            api_id=api_id,
                            api_hash=api_hash,
                            proxy=proxy,
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
        try:
            await client.send_code_request(phone)
            code = input(f"[{session_name} : {phone}] Введите код из Telegram: ")
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            await client.sign_in(password=password)
        except BaseException:
            print(f"[{session_name} : {phone}] Не получилось войти ⛔️\n")
            return

    print(f"[{session_name} : {phone}] Вошли успешно ✅\n")

    # Отправить сообщение самому себе
    me = await client.get_me()
    await client.send_message(me.id, f"Сессия **{session_name}** успешно вошла ✅", parse_mode="markdown")
    await client.disconnect()

    with open(f"{path}\\new_sessions.json", encoding="utf-8") as file:
        data = json.load(file)

    data[session_name] = {
            "api_id": api_id,
            "api_hash": api_hash,
            "password": password,
            "phone": phone,
    }

    with open(f"{path}\\new_sessions.json", encoding="utf-8", mode="w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def main():
    with contextlib.suppress(BaseException):
        await db.create_pool()

    proxies_datas = await get_proxies_datas_from_db()
    if not proxies_datas:
        print("Для создания сессий требуется хотя бы один прокси, а в базе данных их 0!")
        return None

    proxy_dict = proxies_datas[0]

    if proxy_dict['proxy_type'] == 'socks5':
        proxy = (socks.SOCKS5, proxy_dict['addr'], proxy_dict['port'], True, proxy_dict['username'],
                      proxy_dict['password'])
    elif proxy_dict['proxy_type'] == 'socks4':
        proxy = (socks.SOCKS4, proxy_dict['addr'], proxy_dict['port'], True, proxy_dict['username'],
                      proxy_dict['password'])
    elif proxy_dict['proxy_type'] == 'http':
        proxy = (socks.HTTP, proxy_dict['addr'], proxy_dict['port'], True, proxy_dict['username'],
                      proxy_dict['password'])
    else:
        print(f"Тип прокси должен быть либо 'socks5', либо 'socks4', или 'http' - {proxy_dict}")
        return None

    print(f"Прокси для создания сессий - {proxy_dict}")

    for acc in accounts:
        await login_account(acc, proxy)
    return None


if __name__ == '__main__':
    asyncio.run(main())
