from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает кнопки вместе с приветственным сообщением"""

    but1 = InlineKeyboardButton(text='Войти как клиент ТТК', callback_data='login_query')
    but2 = InlineKeyboardButton(text='Заключить новый договор', callback_data='new_agreement_query')

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                but1,
                but2
            ]
        ]
    )

    return keyboard


def send_phone_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает кнопку для отправки номера телефона"""

    but1 = KeyboardButton(text='Отправить номер', request_contact=True)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            but1
        ]
    ], resize_keyboard=True, one_time_keyboard=True)

    return keyboard