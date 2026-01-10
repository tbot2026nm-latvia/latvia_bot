from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    name = State()
    surname = State()
    phone = State()
    passport = State()
