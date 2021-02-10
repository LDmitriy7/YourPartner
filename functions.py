from aiogram import types
from loader import users_db
from keyboards import inline_kb

# статусы проектов
PSTATUS_ACTIVE = 'Активен'
PSTATUS_IN_PROGRESS = 'Выполняется'
PSTATUS_COMPLETED = 'Выполнен'

# типы чатов
CHAT_TYPE_CLIENT = 'client'
CHAT_TYPE_WORKER = 'worker'


async def get_balance(user_id: int) -> int:
    account = await users_db.get_account_by_id(user_id)
    balance = account.get('balance', 0) if account else 0
    return balance


async def get_project_status(msg: types.Message) -> str:
    chat = await users_db.get_chat_by_id(msg.chat.id)
    project_id = chat['project_id']
    project = await users_db.get_project_by_id(project_id)
    return project['status']


async def get_chat_type(msg: types.Message) -> str:
    chat = await users_db.get_chat_by_id(msg.chat.id)
    return chat['chat_type']


async def get_main_keyboard(msg: types.Message) -> inline_kb.MainKeyboard:
    # TODO: проверка срока, кнопка refuse_project
    pstatus = await get_project_status(msg)
    chat_type = await get_chat_type(msg)

    call_admin, offer_price, confirm_project, feedback = True, False, False, False

    if pstatus == PSTATUS_ACTIVE and chat_type == CHAT_TYPE_WORKER:
        offer_price = True
    elif pstatus == PSTATUS_IN_PROGRESS and chat_type == CHAT_TYPE_CLIENT:
        confirm_project = True
    elif pstatus == PSTATUS_COMPLETED and chat_type == CHAT_TYPE_CLIENT:
        feedback = True

    return inline_kb.main_kb(call_admin, offer_price, confirm_project, feedback)


if __name__ == '__main__':
    import asyncio

    msg = types.Message()
    chat = types.Chat
    msg.chat = chat
    msg.chat.id = -578665112
    msg.chat.id = -508294412
    func = get_main_keyboard(msg)
    r = asyncio.run(func)
    print(r)
