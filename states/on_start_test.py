from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    WaitAnswer = State()
    HaveAnswer = State()
    WaitUserPassword = State()
    WaitAdminPassword = State()
    WaitConfig = State()
    WaitNewUserPassword = State()
    WaitResults = State()
    AdminSettings = State()
