from filters import find_pair_chat, PSTATUS_IN_PROGRESS
from aiogram import types
from loader import dp, bot
from config import MAIN_ADMIN_ID


@dp.message_handler(find_pair_chat, user_id=MAIN_ADMIN_ID)
async def forward_from_admin(msg: types.Message, pchat_id: int):
    await msg.forward(pchat_id)


