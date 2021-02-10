from loader import users_db, dp
from aiogram import types
from aiogram.dispatcher.filters.filters import BoundFilter
from functions import PSTATUS_ACTIVE, PSTATUS_COMPLETED, PSTATUS_IN_PROGRESS
from functions import CHAT_TYPE_CLIENT, CHAT_TYPE_WORKER
from functions import get_project_status, get_chat_type
from typing import Union

Update = Union[types.Message, types.CallbackQuery]


async def find_pair_chat(update: Update):
    """Try to find a pair group and return it id."""
    if isinstance(update, types.Message):
        chat = update.chat
    else:
        chat = update.message.chat

    if chat.type == 'group':
        chat_dict = await users_db.get_chat_by_id(chat.id)
        if chat_dict:
            return {'pchat_id': chat_dict['pair_id']}
    return False


class ProjectStatus(BoundFilter):
    key = 'pstatus'

    def __init__(self, pstatus: str):
        if pstatus not in [PSTATUS_ACTIVE, PSTATUS_IN_PROGRESS, PSTATUS_COMPLETED]:
            raise ValueError('Invalid project status.')
        self.pstatus = pstatus

    async def check(self, update: Update) -> bool:
        if isinstance(update, types.CallbackQuery):
            msg = update.message
        else:
            msg = update
        pstatus = await get_project_status(msg)
        return pstatus == self.pstatus


class ChatType(BoundFilter):
    key = 'ctype'

    def __init__(self, ctype: str):
        if ctype not in [CHAT_TYPE_CLIENT, CHAT_TYPE_WORKER]:
            raise ValueError('Invalid chat type.')
        self.ctype = ctype

    async def check(self, update: Update) -> bool:
        if isinstance(update, types.CallbackQuery):
            msg = update.message
        else:
            msg = update
        ctype = await get_chat_type(msg)
        return ctype == self.ctype


dp.filters_factory.bind(ProjectStatus, event_handlers=[dp.callback_query_handlers, dp.message_handlers])
dp.filters_factory.bind(ChatType, event_handlers=[dp.callback_query_handlers, dp.message_handlers])
