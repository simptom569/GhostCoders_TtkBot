from aiogram.fsm.state import State, StatesGroup


class ClientState(StatesGroup):
    """Конечный автомат для пользователя"""

    agreement = State()
    number = State()
    address = State()
    request = State()