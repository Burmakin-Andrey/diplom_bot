from db import datdbase as db
from aiogram import executor, types
from loader import dp, bot
from states import UserStates
from aiogram.dispatcher import FSMContext


@dp.message_handler(lambda message: message.text == "Редактировать опрос")
async def get_password(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text=f"Введите пароль администратора.", reply_markup=types.ReplyKeyboardRemove())
    await UserStates.WaitAdminPassword.set()


@dp.message_handler(state=UserStates.WaitAdminPassword)
async def on_start_test(message: types.Message):
    if message.text != "admin":
        await bot.send_message(chat_id=message.chat.id, text=f"Неверный пароль. Попробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Отправить файл конфигурации", "Обновить пароль"]
        keyboard.add(*buttons)
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
