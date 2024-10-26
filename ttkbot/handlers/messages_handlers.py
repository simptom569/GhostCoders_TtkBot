from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import re
import asyncio
from uuid import uuid4

from states.state import ClientState


dp = Router()


async def process_voice_file(file_name: str):
    await asyncio.sleep(15)
    return "Обработка завершена."


@dp.message(F.text, ClientState.agreement)
async def agreement_message(message: Message, bot: Bot, state: FSMContext):
    pattern = r'^516\d{6}$'
    
    if re.match(pattern, message.text):
        await state.set_state(ClientState.request)
        await bot.send_message(message.from_user.id, "Контракт был найден, опишите ваш запрос в текстовом или голосовом формате")


@dp.message(ClientState.request, F.content_type.in_({'text', 'voice'}))
async def request_message(message: Message, bot: Bot):
    if message.content_type == 'voice':
        voice = await bot.download(message.voice)
        file_name = f"audio/{message.from_user.id}_{uuid4()}_voice.ogg"
        
        with open(file_name, 'wb') as f:
            f.write(voice.read())
        task = asyncio.create_task(process_voice_file(file_name))
        status_message = await bot.send_message(message.from_user.id, "Обработка")

        dots = 0
        while not task.done():
            await asyncio.sleep(1)
            dots = (dots + 1) % 4
            await status_message.edit_text(f"Обработка{'.' * dots}")
        
        result = await task

        await status_message.edit_text(result)


@dp.message(ClientState.number, F.content_type.in_({'text', 'contact'}))
async def get_contact_message(message: Message, bot: Bot, state: FSMContext):
    if message.content_type == 'contact':
        await state.set_state(ClientState.address)
        await state.update_data(phone=message.contact.phone_number)
        
        print(message.contact.phone_number)
        await bot.send_message(message.from_user.id, 'Напишите свой адресс', reply_markup=ReplyKeyboardRemove())
    elif message.text:
        pattern = r'^(?:\+7|8)\d{10}$'
        
        if re.match(pattern, message.text):
            await state.set_state(ClientState.address)
            await state.update_data(phone=message.text)
            print(message.text)
            await bot.send_message(message.from_user.id, 'Напишите свой адресс', reply_markup=ReplyKeyboardRemove())
        else:
            await bot.send_message(message.from_user.id, 'Номер введен некорректно, повторите попытку')


@dp.message(ClientState.address, F.text)
async def get_address_message(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(ClientState.request)
    
    await bot.send_message(message.from_user.id, 'Опишите ваш запрос в текстовом или голосовом формате')