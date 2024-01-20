from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot import logging


def start_inline_kb() -> InlineKeyboardMarkup:
    """Return simple inline keyboard with two buttons"""
    buttons = [
        InlineKeyboardButton(text="Вход", callback_data="enter"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def allready_auth_inline_kb() -> InlineKeyboardMarkup:
    """Return simple inline keyboard with two buttons"""
    buttons = [
        InlineKeyboardButton(text="Продолжить", callback_data="enter"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])