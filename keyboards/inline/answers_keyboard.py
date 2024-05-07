from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_answers_keyboard(answers):
    answers = answers.split(',')
    buttons_in_row = 3
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(answers), buttons_in_row):
        row = answers[i:i+buttons_in_row]
        markup.add(*[KeyboardButton(text=answer) for answer in row])
    markup.add(KeyboardButton(text="Подтвердить ответ"))
    return markup
