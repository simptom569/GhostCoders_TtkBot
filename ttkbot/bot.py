from aiogram import Bot, Dispatcher

import asyncio

from storage.storage import SQLiteStorage
from utils import config
from handlers import commands_handlers, keyboards_handlers, messages_handlers


bot = Bot(token=config.token)
dp = Dispatcher(storage=SQLiteStorage('database.db'))

dp.include_routers(
    commands_handlers.dp,
    keyboards_handlers.dp,
    messages_handlers.dp
)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())