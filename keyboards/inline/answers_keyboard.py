from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_answers_keyboard(answers):
    answers = answers.split(',')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for answer in answers:
        markup.add(KeyboardButton(text=answer))
    return markup
