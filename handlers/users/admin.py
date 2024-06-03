from db import datdbase as db
from aiogram import executor, types
from loader import dp, bot
from states import UserStates
from aiogram.dispatcher import FSMContext
import xml.etree.ElementTree as ET


@dp.message_handler(lambda message: message.text == "Функции администратора")
async def get_password(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text=f"Введите пароль администратора.", reply_markup=types.ReplyKeyboardRemove())
    await UserStates.WaitAdminPassword.set()


@dp.message_handler(state=UserStates.WaitAdminPassword)
async def on_start_test(message: types.Message):
    if message.text != "admin":
        await bot.send_message(chat_id=message.chat.id, text=f"Неверный пароль. Попробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons1 = ["Отправить файл конфигурации", "Обновить пароль"]
        buttons2 = ["Получить количество пользователей", "Получить результаты опроса"]
        keyboard.add(*buttons1)
        keyboard.add(*buttons2)
        await message.answer(f"Выберите, что хотите сделать.", reply_markup=keyboard)
        await UserStates.AdminSettings.set()


@dp.message_handler(lambda message: message.text == "Отправить файл конфигурации", state=UserStates.AdminSettings)
async def xml_handler(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"Загрузите файл конфигурации.", reply_markup=types.ReplyKeyboardRemove())
    await UserStates.WaitConfig.set()


@dp.message_handler(lambda message: message.text == "Обновить пароль", state=UserStates.AdminSettings)
async def update_password(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"Введите новый пароль для доступа к боту.", reply_markup=types.ReplyKeyboardRemove())
    await UserStates.WaitNewUserPassword.set()


@dp.message_handler(lambda message: message.text == "Получить количество пользователей", state=UserStates.AdminSettings)
async def get_users_count(message: types.Message):
    users_count, users_id = await db.get_passed_users()
    users = ""
    for user in users_id:
        name = await db.get_user_name(user[0])
        users += f'{name}\n'
    await bot.send_message(chat_id=message.chat.id, text=f"Экспертов прошедших опрос: {users_count}\nСписок экспертов:\n{users}")


@dp.message_handler(lambda message: message.text == "Получить результаты опроса", state=UserStates.AdminSettings)
async def xml_handler(message: types.Message):
    root = ET.Element('answers')
    for question_id in range(2):
         question_id += 1
        answers = [row[0] for row in await db.get_users_answers(question_id)]
        answers = [answer.split(',') for answer in answers]
        answers = [item for sublist in answers for item in sublist]
        answer_counts = {}
        for answer in answers:
            if answer not in answer_counts:
                answer_counts[answer] = 0
            answer_counts[answer] += 1
        print(answer_counts)

        question = ET.SubElement(root, 'question')
        question.set('id', str(question_id))
        q_text = (await db.get_question(question_id))[1]
        question.set('text', q_text)

        for answer, count in answer_counts.items():
            answer_element = ET.SubElement(question, 'answer')
            answer_element.text = answer
            answer_element.set('count', str(count))
    ET.indent(root, space='  ', level=0)
    xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    with open('result.xml', 'wb') as f:
        f.write(xml_string)
    with open('result.xml', 'rb') as f:
        await bot.send_message(message.chat.id, "Вот файл с результатами опроса")
        await bot.send_document(message.chat.id, f)


@dp.message_handler(state=UserStates.WaitNewUserPassword)
async def save_new_password(message: types.Message):
    print(message.text)
    await db.set_password(message.text)
    await bot.send_message(chat_id=message.chat.id, text=f"Новый пароль успешно установлен.", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=UserStates.WaitConfig, content_types=["document"])
async def xml_handler(message: types.Message, state: FSMContext):
    print("xml_handler")
    document = message.document
    file_name = document.file_name
    mime_type = document.mime_type

    if mime_type != "application/xml":
        await message.answer("Данный тип файла не поддерживается.\nПожалуйста пришлите .xml файл.", reply_markup=types.ReplyKeyboardRemove())
        return
    else:
        await document.download("conf.xml")
        await message.answer(f"XML-файл {file_name} успешно сохранен.", reply_markup=types.ReplyKeyboardRemove())
        await db.fill_db_from_xml("conf.xml")
        await state.finish()
