import asyncio
import contextlib
import os

from mailing import main_function_mailing
from database.create_tables import create_tables
from database.functions import add_new_sessions_from_json, add_new_proxies_from_txt
from database.pool import db
from logger import logger


@logger.catch
async def main():
    # Checking and creating necessary files and directories
    path = os.path.abspath("")
    os.makedirs(f"{path}\\sessions/sessions", exist_ok=True)
    os.makedirs(f"{path}\\logs", exist_ok=True)
    for directory, file in [['sessions', 'new_sessions.json'], ['sessions', 'sessions_datas.txt'], ['our_message', 'message_text.txt']]:
        file_path = os.path.join(path, directory, file)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                pass

    # Initializing the database
    try:
        await db.create_pool()
    except BaseException as e:
        logger.exception("[DATABASE] DATA BASE IS NOT CONNECTED, SO PROCESS WILL BE STOPPED!")
        raise e
    else:
        logger.info("[DATABASE] DATA BASE IS SUCCESSFUL CONNECTED!")
        await create_tables()
    await add_new_sessions_from_json()
    await add_new_proxies_from_txt()

    # Starting the mailing cycle function
    await main_function_mailing()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
