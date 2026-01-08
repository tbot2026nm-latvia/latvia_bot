from aiogram.dispatcher.filters.state import State, StatesGroup

class RegisterState(StatesGroup):
    rules = State()
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()
