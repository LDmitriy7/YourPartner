import re
from aiogram.types import InlineKeyboardButton as InlineButton
from aiogram.types import InlineKeyboardMarkup as InlineKeyboard

DEL_MESSAGE_DATA = 'del_message'  # для удаления связанного сообщения

PAY_FOR_PROJECT_PREFIX = 'pay_for_project_'  # для оплаты проекта
CONFIRM_PROJECT_PREFIX = 'confirm_project_'

PAY_FOR_PROJECT_PATTERN = re.compile(f'{PAY_FOR_PROJECT_PREFIX}[0-9]+_[0-9a-f]+')

ALL_PREFIXES = [PAY_FOR_PROJECT_PREFIX, CONFIRM_PROJECT_PREFIX]


def get_payload(text: str) -> str:
    """Delete all possible prefixes and return project_id."""
    payload = text.split()[-1]
    for prefix in ALL_PREFIXES:
        payload = payload.replace(prefix, '')
    return payload


class MainKeyboard(InlineKeyboard):
    call_admin_data = 'call_admin'
    offer_price_data = 'offer_price'
    confirm_project_data = 'confirm_project'
    feedback_data = 'feedback'


def main_kb(call_admin=False, offer_price=False, confirm_project=False, feedback=False):
    keyboard = MainKeyboard(row_width=1)
    buttons = []

    if call_admin:
        buttons.append(InlineButton(
            'Вызвать админа',
            callback_data=keyboard.call_admin_data,
        ))
    if offer_price:
        buttons.append(InlineButton(
            'Предложить цену',
            callback_data=keyboard.offer_price_data,
        ))
    if confirm_project:
        buttons.append(InlineButton(
            'Подтвердить выполнение',
            callback_data=keyboard.confirm_project_data
        ))
    if feedback:
        buttons.append(InlineButton(
            'Оставить отзыв',
            callback_data=keyboard.feedback_data
        ))

    keyboard.add(*buttons)
    return keyboard


def pay_for_project(price: int, project_id: str):
    """Создает кнопки Оплатить(prefix_цена_проект) и Отказаться."""
    keyboard = InlineKeyboard()
    cdata = f'{PAY_FOR_PROJECT_PREFIX}{price}_{project_id}'
    keyboard.row(InlineButton(f'Оплатить {price} грн', callback_data=cdata))
    keyboard.row(InlineButton('Отказаться', callback_data=DEL_MESSAGE_DATA))
    return keyboard


def confirm_project(project_id: str):
    keyboard = InlineKeyboard()
    cdata = f'{CONFIRM_PROJECT_PREFIX}{project_id}'
    keyboard.row(InlineButton('Подтвердить', callback_data=cdata))
    keyboard.row(InlineButton('Отменить', callback_data=DEL_MESSAGE_DATA))
    return keyboard
