from aiogram import executor, types

from db import datdbase as db
from loader import dp, bot
from utils.set_bot_commands import set_default_commands

q_num = 1
q_count = 0


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await db.db_start()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

