from keyboards import inline_kb
from functions import PSTATUS_ACTIVE, PSTATUS_IN_PROGRESS, CHAT_TYPE_CLIENT
import functions as cfuncs
from filters import find_pair_chat
from loader import dp, users_db, bot
from aiogram import types


@dp.callback_query_handler(find_pair_chat, text_startswith=inline_kb.PAY_FOR_PROJECT_PREFIX,
                           pstatus=PSTATUS_ACTIVE, ctype=CHAT_TYPE_CLIENT)
async def pay_for_project(query: types.CallbackQuery, pchat_id: int):
    client_id, msg = query.from_user.id, query.message
    payload_raw = inline_kb.get_payload(query.data)
    price, project_id = payload_raw.split('_')
    price = int(price)

    pair_chat = await users_db.get_chat_by_id(pchat_id)
    worker_id = pair_chat['user_id']
    balance = await cfuncs.get_balance(client_id)

    if price <= balance:
        amount = -price
        await users_db.update_project_price(project_id, price)
        await users_db.update_project_worker(project_id, worker_id)
        await users_db.incr_balance(client_id, amount)
        await users_db.update_project_status(project_id, PSTATUS_IN_PROGRESS)

        await bot.send_message(pchat_id, 'Проект оплачен, приступайте к работе')
        await msg.answer('Проект оплачен, уведомление отправлено автору')
    else:
        await msg.answer('У вас недостаточно средств, пополните баланс')
