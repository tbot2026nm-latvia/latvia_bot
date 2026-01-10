from aiogram.fsm.state import State, StatesGroup

class Register(StatesGroup):
    waiting_agreement = State()
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()
    waiting_admin = State()
