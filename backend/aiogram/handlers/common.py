from datetime import datetime
import pytz
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types, F
from keyboards.simple_row import make_row_keyboard
from messages import sending_messages
from keyboards.simple_fab import (
    get_admin_keyboard_fab,
    get_keyboard_orders_fab,
    get_keyboard_customer_fab,
    OrdersCallbackFactory,
)
from utils import (
    add_telegram,
    get_customer_by_id,
    get_today_orders_by_customer_title,
    get_id_by_customer_title,
    get_id_by_customer_description,
    delivery_order,
    choose_row_keyboard,
)
from bot import logging
from config import ADMIN_USERS, TIMEZONE

router = Router()

pure_choose = ["Вход"]
pure_admin_choose = ["Вход", "Админ"]
# re_registration_choose = ["Продолжить", "Начать сначала"]
continue_choose = ["Продолжить/Обновить"]


class DeliveryState(StatesGroup):
    pure_state = State()
    customer_state = State()
    admin_state = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    choose = choose_row_keyboard(message, pure_choose, pure_admin_choose)
    await message.answer(
        text=sending_messages(message).get("start"),
        reply_markup=make_row_keyboard(choose),
    )
    await state.set_state(DeliveryState.pure_state)


@router.message(DeliveryState.pure_state)
async def pure_state(message: Message, state: FSMContext):
    if message.text.lower() == "вход":
        state_data = await state.get_data()
        customer = state_data.get("customer")
        if customer:
            await message.answer(
                text=sending_messages(message, customer).get("enter_success"),
                # reply_markup=make_row_keyboard(continue_choose),
                reply_markup=get_keyboard_customer_fab(customer),
            )
            await state.set_state(DeliveryState.pure_state)
        else:
            choose = choose_row_keyboard(message, pure_choose, pure_admin_choose)
            await message.answer(
                text=sending_messages(message).get("enter_fail"),
                reply_markup=make_row_keyboard(choose),
            )
            await state.set_state(DeliveryState.pure_state)
    elif message.text.lower() == "отмена":
        await state.clear()
        await message.answer(
            text=sending_messages(message).get("cancel"),
            reply_markup=ReplyKeyboardRemove(),
        )

    elif message.text.lower() == "админ":
        if str(message.from_user.id) not in ADMIN_USERS:
            choose = choose_row_keyboard(message, pure_choose, pure_admin_choose)
            await message.answer(
                text=sending_messages(message).get("admin_fail"),
                reply_markup=make_row_keyboard(choose),
            )
            await state.set_state(DeliveryState.pure_state)
            return
        else:
            await message.answer(
                text=sending_messages(message).get("choose_action"),
                reply_markup=get_admin_keyboard_fab(),
            )
            await state.set_state(DeliveryState.admin_state)
    else:
        customer_id = get_id_by_customer_description(message.text)
        if customer_id.json():
            customer = get_customer_by_id(customer_id.json())
            customer_title = customer.json().get("title")
            data = {
                "telegram_id": message.from_user.id,
                "telegram_name": message.from_user.full_name,
            }
            add_telegram(customer_id.json(), data)
            await message.answer(
                text=sending_messages(message, customer_title).get(
                    "registration_success"
                ),
                # reply_markup=make_row_keyboard(continue_choose),
                reply_markup=get_keyboard_customer_fab(customer_title),
            )
            await state.update_data({"customer": customer_title})
            logging.info(
                f"customer: {message.text.lower()}"
                f" was registered by {message.from_user.full_name}"
                f" with id {message.from_user.id}"
            )
            await state.set_state(DeliveryState.pure_state)
        else:
            await message.answer(
                text=sending_messages(message).get("restart"),
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(DeliveryState.pure_state)


@router.callback_query(OrdersCallbackFactory.filter(F.action == "update_order_table"))
async def get_customer(
    callback: types.CallbackQuery, callback_data: OrdersCallbackFactory
):
    customer = callback_data.value
    orders = get_today_orders_by_customer_title(customer)
    if len(orders["today_orders"]) == 0:
        await callback.message.answer(
            text=sending_messages(callback.message, customer).get(
                "not_delivery_for_today"
            ),
        )
    else:
        await callback.message.answer(
            text=sending_messages(callback.message, customer).get("delivery_for_today"),
            reply_markup=get_keyboard_orders_fab(orders, customer),
        )


@router.callback_query(OrdersCallbackFactory.filter(F.action == "update_order"))
async def callbacks_add_delivery_time_to_order(
    callback: types.CallbackQuery, callback_data: OrdersCallbackFactory
):
    delivery_order(callback_data, callback.from_user.full_name)
    await callback.answer(
        sending_messages(callback.message).get("delivery_for_customer_success")
    )


@router.callback_query(OrdersCallbackFactory.filter(F.action == "delivered"))
async def callbacks_delivery_allready_delivered(
    callback: types.CallbackQuery, callback_data: OrdersCallbackFactory
):
    await callback.answer(
        sending_messages(callback.message).get("delivery_allready_delivered")
    )


@router.callback_query(OrdersCallbackFactory.filter(F.action == "delivered_time"))
async def callbacks_delivery_allready_delivered(
    callback: types.CallbackQuery, callback_data: OrdersCallbackFactory
):
    callback_data_hour = callback_data.value.split("_")[0]
    callback_data_minute = callback_data.value.split("_")[1]
    timezone = pytz.timezone(TIMEZONE)

    current_time = datetime.now(timezone)  # Get the current time

    delivery_time_naive = datetime(
        year=current_time.year,
        month=current_time.month,
        day=current_time.day,
        hour=int(callback_data_hour),
        minute=int(callback_data_minute),
    )

    delivery_time = timezone.localize(delivery_time_naive)

    if delivery_time > current_time:  # Check if delivery time is in the future
        time_difference = delivery_time - current_time
        # to hours and minutes
        hours = int(time_difference.total_seconds()) // 3600
        minutes = int(time_difference.total_seconds() - hours * 3600) // 60
        minutes = f"0{minutes}" if minutes < 10 else minutes
        await callback.answer(
            sending_messages(callback.message, f"{hours}:{minutes}").get(
                "delivery_awating_time"
            )
        )
    elif delivery_time < current_time:  # Check if delivery time is in the past
        time_difference = current_time - delivery_time
        # to hours and minutes
        hours = int(time_difference.total_seconds()) // 3600
        minutes = int(time_difference.total_seconds() - hours * 3600) // 60
        minutes = f"0{minutes}" if minutes < 10 else minutes
        await callback.answer(
            sending_messages(callback.message, f"{hours}:{minutes}").get(
                "delivery_delivered_time"
            )
        )
