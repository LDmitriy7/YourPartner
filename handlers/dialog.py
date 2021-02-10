from aiogram import types

from filters import find_pair_chat
from functions import get_main_keyboard
from loader import bot, dp, users_db
from texts import templates


@dp.message_handler(find_pair_chat, content_types='new_chat_members')
async def send_welcome(msg: types.Message, pchat_id: int):
    """Отправляет вступившему данные о проекте, уведомляет собеседника."""
    project_id = await users_db.get_project_id(msg.chat.id)
    project = await users_db.get_project_by_id(project_id)

    is_client = msg.from_user.id == project['user_id']  # является ли заказчиком проекта
    post_text = templates.form_post_text(project['data'], with_note=is_client)
    keyboard = await get_main_keyboard(msg)

    await msg.answer('<b>Текущий проект:</b>', reply_markup=keyboard)
    await msg.answer(post_text)
    await msg.answer('<b>Ожидайте собеседника...</b>')
    await bot.send_message(pchat_id, '<b>Ваш собеседник вступил в чат. Напишите ему первым.</b>')


@dp.message_handler(find_pair_chat, content_types='left_chat_member')
async def send_bye(msg: types.Message, pchat_id: int):
    await bot.send_message(pchat_id, '<b>Ваш собеседник покинул группу.</b>')


@dp.message_handler(find_pair_chat, content_types='any')
async def forward(msg: types.Message, pchat_id: int):
    """Копирует все сообщения в связанную группу."""
    await msg.copy_to(pchat_id)
