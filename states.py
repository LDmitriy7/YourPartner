from aiogram.dispatcher.filters.state import State, StatesGroup


class MiscStates(StatesGroup):
    ask_price_amount = State()
