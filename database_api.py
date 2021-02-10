"""Класс для асинхронной работы с MongoDB"""

from typing import List, Optional, Union

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

ACCOUNTS = 'accounts'
PROJECTS = 'projects'
BIDS = 'bids'
CHATS = 'chats'
REVIEWS = 'reviews'
WITHDRAWALS = 'withdrawals'

PROJECTS_INDEX = (PROJECTS, ['client_id', 'worker_id', 'data.subject'])  # 3 indexes for PROJECTS
BIDS_INDEX = (BIDS, ['client_id', 'worker_id'])
INDEXES = [PROJECTS_INDEX, BIDS_INDEX]


class MongoClient:
    """Содержит базовые методы для взаимодействия с базой."""

    def __init__(self, host='localhost', port=27017, db_name='users', index=True):
        self._host = host
        self._port = port
        self._db_name = db_name
        self._index = index

        self._mongo: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    async def _get_client(self) -> AsyncIOMotorClient:
        if isinstance(self._mongo, AsyncIOMotorClient):
            return self._mongo

        uri = f'mongodb://{self._host}:{self._port}'
        self._mongo = AsyncIOMotorClient(uri)
        return self._mongo

    async def get_db(self) -> AsyncIOMotorDatabase:
        if isinstance(self._db, AsyncIOMotorDatabase):
            return self._db

        mongo = await self._get_client()
        self._db = mongo.get_database(self._db_name)

        if self._index:
            await self.apply_index(self._db)
        return self._db

    @staticmethod
    async def apply_index(db):
        for index in INDEXES:
            collection, keys = index
            for key in keys:
                await db[collection].create_index(keys=[(key, 1)], background=True)

    async def close(self):
        if self._mongo:
            self._mongo.close()


class MongoGetter(MongoClient):
    """Содержит методы для поиска объектов в базе."""

    async def _get_object(self, collection: str, _filter: dict, many=False) -> Union[dict, List[dict]]:
        db = await self.get_db()
        if many:
            result = [p async for p in db[collection].find(_filter)]
        else:
            result = await db[collection].find_one(_filter)
        return result

    async def get_chat_by_id(self, chat_id: str) -> dict:
        chat = await self._get_object(CHATS, {'_id': chat_id})
        return chat

    async def get_project_by_id(self, project_id: str) -> dict:
        oid = ObjectId(project_id)
        project = await self._get_object(PROJECTS, {'_id': oid})
        return project

    async def get_account_by_id(self, user_id: int) -> dict:
        _filter = {'_id': user_id}
        account = await self._get_object(ACCOUNTS, _filter)
        return account


class MongoUpdater(MongoClient):
    """Содержит методы для обновления объектов в базе."""

    async def _update_object(self, collection: str, _filter: dict, operator: str, update: dict, upsert=False):
        db = await self.get_db()
        await db[collection].update_one(_filter, {operator: update}, upsert)

    async def incr_balance(self, user_id: int, amount: int):
        await self._update_object(ACCOUNTS, {'_id': user_id}, '$inc', {'balance': amount}, True)

    async def update_project(self, project_id: str, update: dict):
        oid = ObjectId(project_id)
        await self._update_object(PROJECTS, {'_id': oid}, '$set', update)

    async def update_project_status(self, project_id: str, new_status: str):
        await self.update_project(project_id, {'status': new_status})

    async def update_project_worker(self, project_id: str, worker_id: int):
        await self.update_project(project_id, {'worker_id': worker_id})

    async def update_project_price(self, project_id: str, new_price: int):
        await self.update_project(project_id, {'data.price': new_price})


class MongoDB(MongoGetter, MongoUpdater):
    """Наследует все наборы методов управления базой."""
