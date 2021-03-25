import re

from aiogram import types

import texts
from config import GROUP_ADMIN_ID
from filters import find_pair_chat
from loader import dp


@dp.message_handler(text_startswith='/')
async def ignore_msg(*_):
    """Ignore messages for another bot."""
    pass


@dp.message_handler(find_pair_chat, user_id=GROUP_ADMIN_ID)
async def forward_from_admin(msg: types.Message, pchat_id: int):
    await msg.forward(pchat_id)


@dp.message_handler(find_pair_chat)
async def forward(msg: types.Message, pchat_id: int):
    """Копирует все сообщения в связанную группу."""
    username = msg.from_user.username
    lower_msg_text = msg.text.lower()
    stop_words = ['cозвон', 'телефон', 'вайбер', 'ватсап', 'whatsapp', 'мессенджер',
                  'e-mail', 'почта', 'электронка', 'напрямую', 'ссылка', 'как найти тебя',
                  'телега', 'как найти тебя', 'telegram', '@', 't.me']

    for word in stop_words:
        if word in lower_msg_text:
            await msg.answer(texts.error_stop_word)
            return

    if username and username.lower() in lower_msg_text:
        await msg.answer(texts.error_username)
    elif re.search(r'(380)?[0-9-–() ]{9,}', lower_msg_text):
        await msg.answer(texts.error_phone)
    else:
        await msg.copy_to(pchat_id)
