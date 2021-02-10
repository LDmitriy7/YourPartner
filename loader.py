from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from config import BOT_TOKEN
from database_api import MongoDB

bot = Bot(BOT_TOKEN, parse_mode='Html')
storage = MongoStorage(db_name='aiogram_fsm2')
dp = Dispatcher(bot, storage=storage)
users_db = MongoDB()
