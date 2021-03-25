from typing import Union

from aiogram import types

from loader import users_db


class QueryPrefix:
    """Check query.data for prefix, return payload without prefix."""

    def __init__(self, qprefix: str):
        self.qprefix = qprefix

    def __call__(self, query: types.CallbackQuery) -> Union[dict, bool]:
        cdata = query.data
        if cdata.startswith(self.qprefix):
            payload = cdata.removeprefix(self.qprefix)
            return {'payload': payload}
        else:
            return False


async def find_pair_chat(*_) -> Union[dict, bool]:
    """Try to find a pair chat (group) and return it id ('pchat_id')."""
    chat = types.Chat.get_current()
    if chat.type == 'group':
        chat_obj = await users_db.get_chat_by_id(chat.id)
        if chat_obj:
            return {'pchat_id': chat_obj.pair_id}
    return False
