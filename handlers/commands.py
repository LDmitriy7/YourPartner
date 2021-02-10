from loader import dp, users_db, bot
from aiogram import types
from functions import get_main_keyboard
from functions import PSTATUS_ACTIVE, PSTATUS_IN_PROGRESS, PSTATUS_COMPLETED, CHAT_TYPE_CLIENT, CHAT_TYPE_WORKER
from filters import find_pair_chat
from keyboards.inline_kb import MainKeyboard
from keyboards import inline_kb
from config import MAIN_ADMIN_ID
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


class MiscStates(StatesGroup):
    ask_price = State()


@dp.message_handler(text='Отменить', state='*')
@dp.message_handler(commands='cancel', state='*')
async def cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer('Отменено')


@dp.callback_query_handler(text=inline_kb.DEL_MESSAGE_DATA)
async def delete_msg(query: types.CallbackQuery):
    await query.message.delete()


@dp.message_handler(commands='menu')
async def send_keyboard(msg: types.Message):
    keyboard = await get_main_keyboard(msg)
    await msg.answer('Доступные команды:', reply_markup=keyboard)


@dp.callback_query_handler(find_pair_chat, text=MainKeyboard.call_admin_data)
async def call_admin(query: types.CallbackQuery, pchat_id: int):
    msg = query.message
    chat = await users_db.get_chat_by_id(msg.chat.id)
    await bot.send_message(MAIN_ADMIN_ID, f'Вас вызывают в чат: {chat["link"]}')
    await query.answer('Вы вызвали администратора, ожидайте...')
    await bot.send_message(pchat_id, '<b>Ваш собеседник вызвал администратора.</b>')


@dp.callback_query_handler(pstatus=PSTATUS_ACTIVE, ctype=CHAT_TYPE_WORKER, text=MainKeyboard.offer_price_data)
async def ask_price(query: types.CallbackQuery):
    await query.answer()
    await MiscStates.ask_price.set()
    await query.message.answer('Введите цену (в гривнах):')


@dp.message_handler(find_pair_chat, pstatus=PSTATUS_ACTIVE, ctype=CHAT_TYPE_WORKER, state=MiscStates.ask_price)
async def offer_price(msg: types.Message, pchat_id: int, state: FSMContext):
    if msg.text.isdigit():
        price = int(msg.text)
        chat = await users_db.get_chat_by_id(msg.chat.id)
        project_id = chat['project_id']
        text = f'Автор предлагает вам сделку за <b>{price} грн</b>'
        keyboard = inline_kb.pay_for_project(price, project_id)
        await bot.send_message(pchat_id, text, reply_markup=keyboard)
        await msg.answer('Заявка отправлена, мы пришлем вам уведомление в случае оплаты.')
        await state.finish()
    else:
        await msg.answer('Ошибка, отправьте число')


@dp.callback_query_handler(text=MainKeyboard.confirm_project_data,
                           pstatus=PSTATUS_IN_PROGRESS, ctype=CHAT_TYPE_CLIENT)
async def ask_confirm_project(query: types.CallbackQuery):
    msg = query.message
    chat = await users_db.get_chat_by_id(msg.chat.id)
    project_id = chat['project_id']
    text = 'Вы точно хотите подтвердить выполнение проекта?'
    keyboard = inline_kb.confirm_project(project_id)
    await msg.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(find_pair_chat, text_startswith=inline_kb.CONFIRM_PROJECT_PREFIX,
                           pstatus=PSTATUS_IN_PROGRESS, ctype=CHAT_TYPE_CLIENT)
async def confirm_project(query: types.CallbackQuery, pchat_id: int):
    msg = query.message  # TODO: изменеие цены проекта и исполнителя
    project_id = inline_kb.get_payload(query.data)
    project = await users_db.get_project_by_id(project_id)
    price = project['data']['price']
    worker_id = project['worker_id']

    await users_db.update_project_status(project_id, PSTATUS_COMPLETED)
    await users_db.incr_balance(worker_id, price)
    client_text = 'Выполнение проекта подтверждено, вы можете написать отзыв'
    worker_text = 'Заказчик подтвердил выполнение проекта, деньги перечислены на ваш счет.'
    await msg.answer(client_text)
    await bot.send_message(pchat_id, worker_text)
