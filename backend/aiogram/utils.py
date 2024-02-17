import requests
from typing import Optional
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from datetime import datetime
import pytz
from bot import logging
from keyboards.simple_fab import OrdersCallbackFactory, get_admin_keyboard_fab
from keyboards.simple_row import make_row_keyboard, make_hidden_row_keyboard
from config import DELIVERY_SERVICE_API_URL, ADMIN_USERS, TIMEZONE


def get_all_customers():
    response = requests.get(DELIVERY_SERVICE_API_URL)
    return response

def get_customer_by_telegram_id(telegram_id: str):
    response = requests.get(
        DELIVERY_SERVICE_API_URL + f"get_customer_by_telegram_id/{telegram_id}"
    )
    return response

def get_customer_by_id(id: str):
    response = requests.get(
        DELIVERY_SERVICE_API_URL + f"{id}"
    )
    return response


def add_telegram(id: str, data: dict):
    response = requests.post(DELIVERY_SERVICE_API_URL + f"add_telegram/{id}", json=data)
    return response


def get_id_by_customer_title(title: str):
    response = requests.get(
        DELIVERY_SERVICE_API_URL + f"get_id_by_customer_title/{title}"
    )
    return response


def get_id_by_customer_description(description: str):
    response = requests.get(
        DELIVERY_SERVICE_API_URL + f"get_id_by_customer_description/{description}"
    )
    return response


def get_all_delivered_orders_for_today():
    response = requests.get(
        DELIVERY_SERVICE_API_URL + f"all_delivered_orders_for_today/"
    )
    return response


def get_all_orders_for_today():
    response = requests.get(
        DELIVERY_SERVICE_API_URL + f"all_orders_for_today/"
    )
    return response


def get_today_orders_by_customer_title(title: str):
    customer_id = requests.get(
        DELIVERY_SERVICE_API_URL + f"get_id_by_customer_title/{title}"
    )
    response = requests.get(DELIVERY_SERVICE_API_URL + f"{customer_id.json()}")
    today_orders = {"today_orders": []}
    if response.status_code == 200:
        all_orders = response.json().get("orders")
        for order in all_orders:
            if order.get("order_day_time").split("T")[0] == str(datetime.now().date()):
                today_orders["today_orders"].append(order)
    today_orders.update({"customer": customer_id.json()})
    return today_orders


def delivery_order(callback_data_time_with_customer_id: OrdersCallbackFactory, telegram_id):
    callback_data_time_with_customer_id_value = callback_data_time_with_customer_id.value
    callback_data_time_with_customer_id_value_split = callback_data_time_with_customer_id_value.split("_")
    order_day_time = datetime.today().replace(
        hour=int(callback_data_time_with_customer_id_value_split[0]), minute=int(callback_data_time_with_customer_id_value_split[1]), second=0
    )
    timezone = pytz.timezone(TIMEZONE)
    delivery_day_time = datetime.now(timezone)
    update_data = {
        "order_day_time": str(order_day_time.strftime("%Y-%m-%d %H:%M:%S")),
        "delivery_day_time": str(delivery_day_time.strftime("%Y-%m-%d %H:%M:%S")),
        "delivered_by": str(telegram_id)
    }
    customer_id = callback_data_time_with_customer_id_value_split[2]
    response = requests.put(
        DELIVERY_SERVICE_API_URL + f"update_order/{customer_id}",
        json=update_data,
    )
    logging.info(f'Customer id: {customer_id} order time updated: {update_data}')
    return response

    
async def is_customer_exist(message: Message, state: FSMContext, re_registration_choose: list) -> bool:
    state_data = await state.get_data()
    if state_data.get("customer"):
        await message.answer(
            text=f"Привет: {message.from_user.full_name}!\n"
            f"Ваше заведение {state_data.get('customer')}",
            reply_markup=make_row_keyboard(re_registration_choose),
        )
        return True
    return False


def choose_row_keyboard(message: Message, customer_row: list, admin_row: list) -> list:
    if str(message.from_user.id) in ADMIN_USERS:
        logging.info(
            f"Admin {message.from_user.full_name} with id {message.from_user.id} has logged in"
        )
        return admin_row
    return customer_row

def format_orders(orders):
    # Создаем словарь для каждого дня недели
    weekly_orders = {i: [] for i in range(7)}
    for order in orders:
        weekly_orders[order["day_of_week"]].append(order["time_of_day"])
    
    # Формируем строки с заказами
    max_length = max(len(day_orders) for day_orders in weekly_orders.values())
    order_lines = []
    for i in range(max_length):
        line = "|"
        for day in range(7):
            if i < len(weekly_orders[day]):
                line += " " + weekly_orders[day][i] + " |"
            else:
                line += " --:-- |"  # Используем маркер для пустого времени
        order_lines.append(line)
    return order_lines

def format_time_to_hour_minute(str_time: str):
    return str_time.split("T")[1].split(".")[0][:-3]

def logging_message():
    def wrapper(func):
        async def wrapped(*args, **kwargs):
            message = args[0]
            logging.info(f"Message from {message.from_user.full_name} with id {message.from_user.id}: {message.text}")
            return await func(*args, **kwargs)
        return wrapped