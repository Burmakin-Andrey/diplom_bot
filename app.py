<<<<<<< HEAD
from aiogram import executor
from db import datdbase as db
from loader import dp
=======
from aiogram import executor, types

from db import datdbase as db
from loader import dp, bot
>>>>>>> e94a3993aea735aa28e21d081036297e4055ab14
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await db.db_start()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

