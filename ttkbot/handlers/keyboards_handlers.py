from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states.state import ClientState
from keyboards.keyboard import send_phone_keyboard


dp = Router()


@dp.callback_query(F.data == 'login_query')
async def login_query(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    await callback_query.answer()
    await state.set_state(ClientState.agreement)
    
    await bot.send_message(callback_query.from_user.id, 'Введите номер договора')


@dp.callback_query(F.data == 'new_agreement_query')
async def new_agreement_query(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    await callback_query.answer()
    await state.set_state(ClientState.number)
    
    await bot.send_message(callback_query.from_user.id, 'Отправьте свой контактный номер\nИли напишите в формате +71234567890 или 81234567890', reply_markup=send_phone_keyboard())