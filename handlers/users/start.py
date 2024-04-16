from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    print("start_bot")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Пройти опрос", "Редактировать опрос"]
    keyboard.add(*buttons)
    await message.answer(f"Здравствуйте!\nВыберите, что хотите сделать.", reply_markup=keyboard)
