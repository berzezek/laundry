import requests
from typing import Optional
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from datetime import datetime
from bot import logging
from keyboards.simple_fab import OrdersCallbackFactory, get_keyboard_fab
from keyboards.simple_row import make_row_keyboard, make_hidden_row_keyboard
from config import DELIVERY_SERVICE_API_URL, ADMIN_USERS


def get_customer_by_telegram_id(telegram_id: str):
    response = requests.get(
        DELIVERY_SERVICE_API_URL + f"get_customer_by_telegram_id/{telegram_id}"
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


def delivery_order(callback_data_time_with_customer_id: OrdersCallbackFactory):
    callback_data_time_with_customer_id_value = callback_data_time_with_customer_id.value
    callback_data_time_with_customer_id_value_split = callback_data_time_with_customer_id_value.split("_")
    order_day_time = datetime.today().replace(
        hour=int(callback_data_time_with_customer_id_value_split[0]), minute=int(callback_data_time_with_customer_id_value_split[1]), second=0
    )
    delivery_day_time = datetime.now()
    update_order_time = {
        "order_day_time": str(order_day_time.strftime("%Y-%m-%d %H:%M:%S")),
        "delivery_day_time": str(delivery_day_time.strftime("%Y-%m-%d %H:%M:%S")),
    }
    customer_id = callback_data_time_with_customer_id_value_split[2]
    response = requests.put(
        DELIVERY_SERVICE_API_URL + f"update_order/{customer_id}",
        json=update_order_time,
    )
    logging.info(f'Customer id: {customer_id} order time updated: {update_order_time}')
    return response


# message functions

async def send_start_message(message: Message, state: FSMContext, authorize_choose: list):
    await state.clear()
    await message.answer(
        text="Здравствуйте зарегистрируйтесь пожалуйста: ",
        reply_markup=make_hidden_row_keyboard(authorize_choose),
    )

async def send_registration_success_message(message: Message, registered_venue: str, re_registration_choose: list):
    await message.answer(
        text=f"Привет: {message.from_user.full_name}!\n"
             f"Вы успешно зарегистрировали заведение: <b>{registered_venue}</b>",
        reply_markup=make_row_keyboard(re_registration_choose),
    )
    
async def send_restart_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=f"Заведение <b>{message.text}</b> не было зарегистрировано!\n"
        "Чтобы начать сначала нажмите /start",
        reply_markup=ReplyKeyboardRemove(),
    )
    
async def is_customer_exist(message: Message, state: FSMContext, re_registration_choose: list) -> bool:
    state_data = await state.get_data()
    if state_data.get("customer"):
        await message.answer(
            text=f"Привет: {message.from_user.full_name}!\n"
            f"Ваше заведение {state_data.get("customer")}",
            reply_markup=make_row_keyboard(re_registration_choose),
        )
        return True
    return False


async def send_admin_start_message(message: Message):
    await message.answer(
        text="Здравствуйте, Admin!",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        text="Выберите действие:",
        reply_markup=get_keyboard_fab(),
    )

def choose_row_keyboard(message: Message, customer_row: list, admin_row: list) -> list:
    if str(message.from_user.id) in ADMIN_USERS:
        logging.info(
            f"Admin {message.from_user.full_name} with id {message.from_user.id} has logged in"
        )
        return admin_row
    return customer_row