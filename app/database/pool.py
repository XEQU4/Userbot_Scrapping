import asyncpg
import os

from asyncpg import Pool
from dotenv import load_dotenv


class CreatePool:

    def __init__(self, dsn: str):
        """
        :param dsn: str - 'postgres://<user>:<password>@<host>:<port>/<database>'
        """
        self.config = dsn
        self._pool = None  # Pool object

    async def get_pool(self) -> Pool:
        """
        :return: Pool object
        """
        return self._pool

    async def create_pool(self) -> None:
        """
        Create and save the Pool object in the class CreatePool
        """
        self._pool = await asyncpg.create_pool(dsn=self.config)


load_dotenv()
db = CreatePool(os.getenv("DSN"))  # DataBase Object

