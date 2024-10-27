from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

import re
import asyncio
from uuid import uuid4

from states.state import ClientState
from utils import config

import aiohttp


dp = Router()


async def process_voice_file(file_name: str):
    url = "http://127.0.0.1:8000/api/v1/audio-intent/"
    headers = {
        "Authorization": "Token " + config.token_auth,
    }

    # Чтение и отправка файла на сервер
    async with aiohttp.ClientSession() as session:
        with open(file_name, 'rb') as f:
            data = {'audio': f}
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    return f"Ошибка при обработке: {response.status} - {response.reason}"


async def process_text_message(text_message: str, user_id: int):
    url = "http://127.0.0.1:8000/api/v1/text-intent/"
    headers = {
        "Authorization": "Token " + config.token_auth,
    }
    data = {'text': text_message, 'id': user_id}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                if 'error' in result:
                    return f"Ошибка от сервера: {result['error']}"
                return result.get('response', "Ответ не найден.")
            else:
                return f"Ошибка при обработке: {response.status} - {response.reason}"




async def create_user(telegram_id: int, agreement: str = None, phone: str = None, address: str = None):
    """
    Функция для отправки POST-запроса на создание пользователя на сервере.
    """
    url = "http://127.0.0.1:8000/api/v1/users/"
    headers = {
        "Authorization": "Token " + config.token_auth,
    }
    data = {
        "id": telegram_id,
        "phone": phone,
        "address": address
    }
    # Добавляем `agreement`, только если он не None
    if agreement is not None:
        data["agreement"] = agreement
    print(data)

    # Отправка запроса на сервер
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status in (200, 201):
                return "Пользователь успешно создан на сервере."
            else:
                error_text = await response.text()
                return f"Ошибка при создании пользователя: {response.status} - {error_text}"


@dp.message(F.text, ClientState.agreement)
async def agreement_message(message: Message, bot: Bot, state: FSMContext):
    pattern = r'^516\d{6}$'
    
    if re.match(pattern, message.text):
        await state.set_state(ClientState.request)
        # запрос на создание
        # Отправлять номер контрактка!!!! id = tg id . Контракт получаю message.text()
        # id получаю message.from_user.id

        # Создаем пользователя на сервере
        # Отправка запроса на создание пользователя с telegram_id и agreement
        telegram_id = message.from_user.id
        agreement = message.text
        creation_result = await create_user(telegram_id=telegram_id, agreement=agreement)
        # await bot.send_message(message.from_user.id, creation_result)

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
        print(result)

        # Проверяем, что result является словарем и содержит 'response'
        if isinstance(result, dict) and 'response' in result:
            response_message = result['response'] if result['response'] is not None else "Ответ не найден."
        else:
            response_message = "Произошла ошибка при обработке запроса."

        await status_message.edit_text(response_message)

    elif message.content_type == 'text':
        text_message = message.text  # Получаем текст сообщения
        response_message = await process_text_message(text_message, message.from_user.id)
        await bot.send_message(message.from_user.id, response_message)
        

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
    
    user_data = await state.get_data()
    telegram_id = message.from_user.id
    phone = user_data.get('phone')
    address = message.text

    # Отправка запроса на создание пользователя с telegram_id, phone и address
    creation_result = await create_user(telegram_id=telegram_id, phone=phone, address=address)
    # await bot.send_message(message.from_user.id, creation_result)

    await bot.send_message(message.from_user.id, 'Опишите ваш запрос в текстовом или голосовом формате')