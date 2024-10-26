from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import keyboard


dp = Router()


@dp.message(CommandStart())
async def start(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, 'Приветсвенное сообщение', reply_markup=keyboard.start_keyboard())