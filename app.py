from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart

from db import datdbase as db
from keyboards.inline.answers_keyboard import make_answers_keyboard
from loader import dp, bot
from states import UserStates
from utils.set_bot_commands import set_default_commands

q_num = 1
q_count = 0


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await db.db_start()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    print("start_bot")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Пройти опрос", "Редактировать опрос"]
    keyboard.add(*buttons)
    await message.answer(f"Здравствуйте!\nВыберите, что хотите сделать.", reply_markup=keyboard)


@dp.message_handler(Command('about'))
async def about(message: types.Message):
    text = """Scenic Spots - это сайт-фотогалерея, который позволит вам узнать о новых местах, куда сходить, куда прогуляться, он выдаст вам полезную информацию о том где это, покажет как туда добраться и адрес. Также покажет фотографии из этого места."""
    await message.answer(text=text)


async def ask_question(chat_id, q_num, q_count):
    print("Start test")

    if q_num <= q_count:
        quest = await (db.get_question(q_num))
        photo = await db.get_photo(q_num)
        await bot.send_photo(chat_id=chat_id, photo=photo[0], caption=f"Вопрос №{q_num}:\n {quest[1]}", reply_markup=make_answers_keyboard(quest[2]))
        await UserStates.WaitAnswer.set()
    else:
        await bot.send_message(chat_id=chat_id, text=f"Это был последний вопрос. \n Спасибо, что приняли участие.")


@dp.message_handler(lambda message: message.text == "Пройти опрос")
async def on_start_test(message: types.Message):
    id = message.from_user.id
    global q_count
    await db.db_start()
    await db.test_data()
    await db.check_user(id)
    q_count = await db.questions_count()
    await ask_question(message.chat.id, q_num, q_count)


@dp.message_handler(state=UserStates.WaitAnswer)
async def tower(message: types.Message, state: FSMContext):
    global q_num
    global q_count
    print(f'q_num in text_hand={q_num}')
    await db.set_answers(message.from_user.id, q_num, message.text)
    q_num += 1
    await state.finish()
    await ask_question(message.chat.id, q_num, q_count)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

