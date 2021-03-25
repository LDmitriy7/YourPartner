"""Класс для асинхронной работы с MongoDB"""

from dataclasses import asdict
from typing import List, Optional, Union

from aiogram.utils.helper import Helper
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.results import InsertOneResult

import data_classes

ACCOUNTS = 'accounts'
PROJECTS = 'projects'
BIDS = 'bids'
CHATS = 'chats'
REVIEWS = 'reviews'
WITHDRAWALS = 'withdrawals'


class Indexes(Helper):
    PROJECTS = (PROJECTS, ['client_id', 'worker_id', 'data.subject'])
    BIDS = (BIDS, ['client_id', 'worker_id'])


class MongoClient:
    """Содержит методы управления MongoDB клиентом."""

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
        for index in Indexes.all():
            collection, fields = index
            for field in fields:
                await db[collection].create_index(keys=[(field, 1)], background=True)

    async def close(self):
        if self._mongo:
            self._mongo.close()


class MongoBase(MongoClient):
    """Содержит базовые методы для взаимодействия с базой данных."""

    async def add_object(self, collection: str, object_data: dict) -> str:
        """Добавляет объект в коллекцию, возращает его _id."""
        db = await self.get_db()
        if object_data.get('_id') is None:
            object_data.pop('_id', None)
        result: InsertOneResult = await db[collection].insert_one(object_data)
        return str(result.inserted_id)

    async def get_object(self, collection: str, _filter: dict,
                         many=False) -> Union[dict, List[dict], None]:
        """Возвращает из коллекции объект, список объектов [many=True] или None."""
        db = await self.get_db()
        if many:
            result = [obj async for obj in db[collection].find(_filter) if obj]
        else:
            result = await db[collection].find_one(_filter)
        return result

    async def delete_object(self, collection: str, _filter: dict):
        """Удаляет объект из коллекции."""
        db = await self.get_db()
        await db[collection].delete_one(_filter)

    async def update_object(self, collection: str, _filter: dict, operator: str, update: dict, upsert=True):
        """Обновляет элемент коллекции, может создать новый элемент при [upsert=True]."""
        db = await self.get_db()
        await db[collection].update_one(_filter, {operator: update}, upsert)


class MongoAdder(MongoBase):
    """Содержит методы для добавления объектов в коллекции."""

    async def add_project(self, project: data_classes.Project) -> str:
        return await self.add_object(PROJECTS, asdict(project))

    async def add_bid(self, bid: data_classes.Bid) -> str:
        return await self.add_object(BIDS, asdict(bid))

    async def add_chat(self, chat: data_classes.Chat) -> str:
        return await self.add_object(CHATS, asdict(chat))

    async def add_review(self, review: data_classes.Review) -> str:
        return await self.add_object(REVIEWS, asdict(review))


class MongoGetter(MongoBase):
    """Содержит методы для поиска объектов в коллекциях."""

    async def get_all_accounts(self) -> List[data_classes.Account]:
        accounts = []
        for a in await self.get_object(ACCOUNTS, {}, many=True):
            account = data_classes.Account.from_dict(a)
            accounts.append(account)
        return accounts

    async def get_all_projects(self) -> List[data_classes.Project]:
        projects = []
        for p in await self.get_object(PROJECTS, {}, many=True):
            project = data_classes.Project.from_dict(p)
            projects.append(project)
        return projects

    async def get_project_by_id(self, project_id: str) -> Optional[data_classes.Project]:
        _filter = {'_id': ObjectId(project_id)}
        project_dict = await self.get_object(PROJECTS, _filter)
        return data_classes.Project.from_dict(project_dict)

    async def get_projects_by_user(self, client_id: int = None, worker_id: int = None) -> List[data_classes.Project]:
        if client_id:
            _filter = {'client_id': client_id}
        elif worker_id:
            _filter = {'worker_id': worker_id}
        else:
            raise ValueError('Must specify one of values.')

        projects = []
        for p in await self.get_object(PROJECTS, _filter, many=True):
            project = data_classes.Project.from_dict(p)
            projects.append(project)
        return projects

    async def get_projects_by_subjects(self, subjects: List[str], only_active=True) -> List[data_classes.Project]:
        _filter = {'data.subject': {'$in': subjects}}
        if only_active:
            _filter.update(status='Активен')
        projects = []
        for p in await self.get_object(PROJECTS, _filter, many=True):
            project = data_classes.Project.from_dict(p)
            projects.append(project)
        return projects

    async def get_account_by_id(self, user_id: int) -> Optional[data_classes.Account]:
        _filter = {'_id': user_id}
        account = await self.get_object(ACCOUNTS, _filter)
        return data_classes.Account.from_dict(account)

    async def get_chat_by_id(self, chat_id: int) -> Optional[data_classes.Chat]:
        _filter = {'_id': chat_id}
        chat = await self.get_object(CHATS, _filter)
        return data_classes.Chat.from_dict(chat)

    async def get_bid_by_id(self, bid_id: str) -> Optional[data_classes.Bid]:
        _filter = {'_id': ObjectId(bid_id)}
        bid = await self.get_object(BIDS, _filter)
        return data_classes.Bid.from_dict(bid)

    async def get_reviews_by_worker(self, worker_id: int) -> List[data_classes.Review]:
        reviews = []
        for r in await self.get_object(REVIEWS, {'worker_id': worker_id}, many=True):
            reviews.append(data_classes.Review.from_dict(r))
        return reviews


class MongoDeleter(MongoBase):
    """Содержит методы для удаления объектов из коллекций."""

    async def delete_project_by_id(self, project_id: str):
        _filter = {'_id': ObjectId(project_id)}
        await self.delete_object(PROJECTS, _filter)

    async def delete_account_by_id(self, user_id: int):
        _filter = {'_id': user_id}
        await self.delete_object(ACCOUNTS, _filter)

    async def delete_bid_by_id(self, bid_id: str):
        _filter = {'_id': ObjectId(bid_id)}
        await self.delete_object(BIDS, _filter)

    async def delete_chat_by_id(self, chat_id: int):
        _filter = {'_id': chat_id}
        await self.delete_object(CHATS, _filter)


class MongoUpdater(MongoBase):
    """Содержит методы для обновления объектов в коллекциях."""

    async def incr_balance(self, user_id: int, amount: int):
        await self.update_object(ACCOUNTS, {'_id': user_id}, '$inc', {'balance': amount})

    async def update_account_subjects(self, user_id: int, subjects: List[str]):
        _filter = {'_id': user_id}
        await self.update_object(ACCOUNTS, _filter, '$set', {'subjects': subjects})

    async def update_account_profile(self, user_id: int, profile: data_classes.Profile):
        _filter = {'_id': user_id}
        await self.update_object(ACCOUNTS, _filter, '$set', {'profile': asdict(profile)})

    async def update_account_page_url(self, user_id: int, page_url: str):
        _filter = {'_id': user_id}
        await self.update_object(ACCOUNTS, _filter, '$set', {'page_url': page_url}, upsert=False)

    async def update_profile(self, user_id: int, profile_field: str, new_value):
        _filter = {'_id': user_id}
        await self.update_object(ACCOUNTS, _filter, '$set', {f'profile.{profile_field}': new_value})

    async def update_project(self, project_id: str, field: str, new_value):
        _filter = {'_id': ObjectId(project_id)}
        await self.update_object(PROJECTS, _filter, '$set', {field: new_value}, upsert=False)

    async def update_project_data(self, project_id: str, data_field: str, new_value):
        await self.update_project(project_id, f'data.{data_field}', new_value)


class MongoProjectUpdater(MongoUpdater):
    """Содержит методы для обновления данных проекта."""

    async def update_project_status(self, project_id: str, new_status: str):
        await self.update_project(project_id, 'status', new_status)

    async def update_project_post_url(self, project_id: str, post_url: str):
        await self.update_project(project_id, 'post_url', post_url)

    async def update_project_worker(self, project_id: str, worker_id: int):
        await self.update_project(project_id, 'worker_id', worker_id)

    async def update_project_chats(self, project_id: str, client_chat_id: int, worker_chat_id: int):
        await self.update_project(project_id, 'client_chat_id', client_chat_id)
        await self.update_project(project_id, 'worker_chat_id', worker_chat_id)

    async def update_project_price(self, project_id: str, price: int):
        await self.update_project_data(project_id, 'price', price)


class MongoProfileUpdater(MongoUpdater):
    """Содержит методы для обновления профиля аккаунта."""

    async def update_profile_nickname(self, user_id: int, nickname: str):
        await self.update_profile(user_id, 'nickname', nickname)

    async def update_profile_phone_number(self, user_id: int, phone_number: str):
        await self.update_profile(user_id, 'phone_number', phone_number)

    async def update_profile_email(self, user_id: int, email: str):
        await self.update_profile(user_id, 'email', email)

    async def update_profile_biography(self, user_id: int, biography: str):
        await self.update_profile(user_id, 'biography', biography)

    async def update_profile_works(self, user_id: int, works: List[str]):
        await self.update_profile(user_id, 'works', works)


class MongoDB(MongoAdder, MongoGetter, MongoDeleter,
              MongoProjectUpdater, MongoProfileUpdater):
    """Наследует все наборы методов управления базой."""
