# import asyncio
# import json
# import os
# import random
#
# import socks
# from telethon import TelegramClient
# from telethon.errors import SessionPasswordNeededError
# from telethon import functions, types
#
# path = os.path.abspath("") + "\\sessions"
# sessions_names_list = [session_name_fl.rstrip(".session") for session_name_fl in os.listdir(f"{path}\\sessions")]
#
# with open(f"{path}\\sessions_datas.txt") as f:
#     accounts_list = f.readlines()[1:]
#     accounts: list[dict] = []
#
#     for account_string in accounts_list:
#         account_list = account_string.strip().split("/")
#
#         accounts.append({
#             "session_name": account_list[0],
#             "api_id": int(account_list[1]),
#             "api_hash": account_list[2],
#             "password": account_list[3],
#             "phone": account_list[4],
#         })
#
#
# async def login_account(account):
#     await asyncio.sleep(random.uniform(0.5, 1.5))
#     session_name = account['session_name']
#     session_path = f"{path}\\sessions\\{session_name}.session"
#     api_id = account['api_id']
#     api_hash = account['api_hash']
#     phone = account['phone']
#     password = account['password']
#     print(f"[{session_name}] Проверка авторизации. Сессия: {account}")
#
#     client = TelegramClient(session_path, api_id, api_hash, proxy=(socks.HTTP, '185.220.35.151', 40040, True, 'bmKjt9', 'KYDjmZ'), timeout=3, request_retries=5)
#     try:
#         async with client:
#             receiver = await client.get_input_entity('https://t.me/test_my_bots3')
#             all_participants = await client.get_participants(receiver)
#         user_ids = [user.id for user in all_participants]
#     except Exception as e:
#         print("ERROR")
#     print(user_ids)
#
#     # result = await client(functions.messages.SendMediaRequest(
#     #     peer=1246447253,
#     #     message='***Hello, world***',
#     #     media=types.InputMediaUploadedPhoto(
#     #         file=await client.upload_file(r'C:\Users\barah\MyProjects\PythonProjects\UserbotChatbot_ScrappingMailingAnalyzing\Userbot_Scrapping\our_message\image.jpg')
#     #     )
#     # ))
#
#     # result = await client.send_file(
#     #     entity=1246447253,
#     #     file=r"C:\Users\barah\MyProjects\PythonProjects\UserbotChatbot_ScrappingMailingAnalyzing\Userbot_Scrapping\our_message\image.jpg",
#     #     caption="__**Hello, world!**__",
#     #     parse_mode="markdown"
#     # )
#
#     # from telethon.tl.functions.messages import ImportChatInviteRequest
#     # # entity = await client.get_entity(-4640402872)
#     # result = await client(functions.channels.JoinChannelRequest(
#     #     channel='cdsvsvsv'
#     # ))
#     # print(result.stringify())
#
#     await client.disconnect()
#
#
# async def main():
#     await login_account(accounts[0])
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
# # #
# # # # proxy_data = {
# # # #     'proxy_type': 'socks5', # (mandatory) protocol to use (see above)
# # # #     'addr': '1.1.1.1',      # (mandatory) proxy IP address
# # # #     'port': 5555,           # (mandatory) proxy port number
# # # #     'username': 'foo',      # (optional) username if the proxy requires auth
# # # #     'password': 'bar',      # (optional) password if the proxy requires auth
# # # #     'rdns': True            # (optional) whether to use remote or local resolve, default remote
# # # # }
# # # # filtered_proxy_data = {k: v for k, v in proxy_data.items() if k != "rdns"}
# # # # print(filtered_proxy_data)
# # #
# # # a = 5
# # # print(a // 6)
# import os
# path = os.path.abspath("") + "\\"
# # with open(f"{path}sessions\\proxies_datas.txt", encoding="utf-8") as file:
# #     data = [proxy_str.rstrip('\n') for proxy_str in file.readlines()[1:] if proxy_str.rstrip('\n')]
# # print(data)
# print(os.listdir(f"{path}our_message"))