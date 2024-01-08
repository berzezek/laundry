from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

class OrdersCallbackFactory(CallbackData, prefix="ordersfab"):
    action: Optional[str] = None
    value: Optional[str] = None


def get_keyboard_orders_fab(orders: list):
    builder = InlineKeyboardBuilder()
    for order in orders['today_orders']:
        order_hour_minute = str(order['order_day_time'].split("T")[1].split(".")[0][:-3])
        builder.button(text=order_hour_minute, callback_data=OrdersCallbackFactory(action="delivered_time", value=order_hour_minute.replace(":", "_")))
        if order['delivery_day_time']:
            builder.button(text="Доставлено", callback_data=OrdersCallbackFactory(action="delivered"))
        else:
            callback_data_time_with_customer_id = f"{order_hour_minute.replace(":", "_")}_{orders['customer']}"
            builder.button(text="Получить", callback_data=OrdersCallbackFactory(action="update_order", value=callback_data_time_with_customer_id))
        builder.adjust(2)
    return builder.as_markup()

def get_admin_keyboard_fab():
    builder = InlineKeyboardBuilder()
    # builder.button(text="Добавить Заказчика", callback_data=OrdersCallbackFactory(action="add_customer"))
    # builder.button(text="Добавить Расписание", callback_data=OrdersCallbackFactory(action="add_schedule"))
    builder.button(text="Показать статистику", callback_data=OrdersCallbackFactory(action="get_statistic"))
    builder.button(text="Скачать статистику", callback_data=OrdersCallbackFactory(action="download_statistic"))
    builder.adjust(2)
    return builder.as_markup()
