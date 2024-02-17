from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
import time

class OrdersCallbackFactory(CallbackData, prefix="ordersfab"):
    action: Optional[str] = None
    value: Optional[str] = None


def get_keyboard_customer_fab(customer):
    builder = InlineKeyboardBuilder()
    builder.button(text="Продолжить", callback_data=OrdersCallbackFactory(action="update_order_table", value=customer))
    return builder.as_markup()


def get_keyboard_orders_fab(orders: list, customer: str):
    builder = InlineKeyboardBuilder()
    for order in orders['today_orders']:
        order_hour_minute = str(order['order_day_time'].split("T")[1].split(".")[0][:-3])
        builder.button(text=order_hour_minute, callback_data=OrdersCallbackFactory(action="delivered_time", value=order_hour_minute.replace(":", "_")))
        if order['delivery_day_time'] and order['delivered_by']:
            builder.button(text=f"\u2713 {order['delivery_day_time'].split('T')[1].split('.')[0][:-3]} - {order['delivered_by']}", callback_data=OrdersCallbackFactory(action="delivered"))
        else:
            callback_data_time_with_customer_id = f'{order_hour_minute.replace(":", "_")}_{orders["customer"]}'
            builder.button(text="Получить", callback_data=OrdersCallbackFactory(action="update_order", value=callback_data_time_with_customer_id))
    builder.button(text="Обновить", callback_data=OrdersCallbackFactory(action="update_order_table", value=customer))
    builder.adjust(2)
    return builder.as_markup()

def get_admin_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(text="Показать статистику", callback_data=OrdersCallbackFactory(action="get_statistic"))
    builder.button(text="Показать расписание", callback_data=OrdersCallbackFactory(action="periodic_orders"))
    builder.button(text="Скачать статистику", callback_data=OrdersCallbackFactory(action="download_statistic"))
    # builder.button(text="Скачать расписание", callback_data=OrdersCallbackFactory(action="get_schedule"))
    builder.adjust(2)
    return builder.as_markup()
