from datetime import datetime
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from keyboards.inline_kb import start_inline_kb, allready_auth_inline_kb
from bot import logging

router = Router()

class CustomerState(StatesGroup):
    start_authorize = State()
    authorized = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text="Здравствуйте, Введите наименование заведения:",
        reply_markup=start_inline_kb(),
    )
    await state.set_state(CustomerState.start_authorize)
    
@router.callback_query(F.data.lower() == "продолжить")
async def enter_callback(callback_query: CallbackQuery):
    logging.info("Enter callback")
    await callback_query.answer("Вы нажали кнопку Вход")
    await state.set_state(CustomerState.start_authorize)
    
@router.callback_query(F.data.lower() == "enter")
async def enter_callback(callback_query: CallbackQuery):
    logging.info("Enter callback")
    await callback_query.answer("Вы нажали кнопку Вход")
    
@router.callback_query(F.data == "cancel")
async def cancel_callback(callback_query: CallbackQuery):
    logging.info("Cancel callback")
    await callback_query.answer("Вы нажали кнопку Отмена")