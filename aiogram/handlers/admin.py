from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards.simple_fab import get_keyboard_fab
from bot import logging

router = Router()


@router.message(Command(commands=["admin"]))
async def admin_start(message: Message):
    await message.answer(
        text="Здравствуйте, Admin!",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        text="Выберите действие:",
        reply_markup=get_keyboard_fab(),
    )
