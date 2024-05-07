from aiogram.dispatcher import FSMContext
from keyboards.inline.answers_keyboard import make_answers_keyboard
from db import datdbase as db
from loader import dp, bot
from aiogram import types
from states import UserStates

q_num = 1
q_count = 0
answers_list = []


async def ask_question(chat_id, q_num, q_count):
    print("Start test")

    if q_num <= q_count:
        quest = await (db.get_question(q_num))
        photo = await db.get_photo(q_num)
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=f"Вопрос №{q_num}:\n{quest[1]}", reply_markup=make_answers_keyboard(quest[2]))
        await UserStates.WaitAnswer.set()
    else:
        await bot.send_message(chat_id=chat_id, text=f"Это был последний вопрос.\nСпасибо, что приняли участие.", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Пройти опрос")
async def get_password(message: types.Message):
    valid = await db.check_user(message.from_user.id)
    if valid:
        global q_count
        q_count = await db.questions_count()
        await ask_question(message.chat.id, q_num, q_count)
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f"Введите пароль для начала опроса.", reply_markup=types.ReplyKeyboardRemove())
        await UserStates.WaitUserPassword.set()


@dp.message_handler(state=UserStates.WaitUserPassword)
async def on_start_test(message: types.Message, state: FSMContext):
    password = await db.get_password()
    if message.text != password:
        await bot.send_message(chat_id=message.chat.id, text=f"Неверный пароль. Попробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
    else:
        id = message.from_user.id
        global q_count
        await db.check_user(id, True)
        q_count = await db.questions_count()
        await ask_question(message.chat.id, q_num, q_count)


@dp.message_handler(state=UserStates.WaitAnswer)
async def save_answer(message: types.Message, state: FSMContext):
    global q_num
    global q_count
    global answers_list
    if message.text != "Подтвердить ответ":
        answers_list.append(message.text)
        return
    await db.set_answers(message.from_user.id, q_num, answers_list)
    answers_list = []
    q_num += 1
    await state.finish()
    await ask_question(message.chat.id, q_num, q_count)
