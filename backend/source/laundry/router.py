from fastapi import APIRouter
from typing import Optional, List, Dict
from source.laundry.models import (
    CustomerCRUD,
    CustomerModel,
    CustomerCollection,
    UpdateCustomerModel,
    DailyOrderModel,
    OrdersModel,
    UpdateOrdersModel,
    TelegramModel,
)
from source.database import delivery_collection

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.get("/")
async def index():
    response = await CustomerCRUD(CustomerCollection).get_data(delivery_collection)
    return response


@router.get("/{id}")
async def get_by_id(id: str):
    response = await CustomerCRUD(CustomerModel).get_data_id(id, delivery_collection)
    return response


@router.post("/")
async def create(data: CustomerModel):
    response = await CustomerCRUD(CustomerModel).create_data(data, delivery_collection)
    return response


@router.put("/{id}")
async def update(id: str, data: UpdateCustomerModel):
    response = await CustomerCRUD(UpdateCustomerModel).update_data(
        id, data, delivery_collection
    )
    return response


@router.delete("/{id}")
async def delete(id: str):
    response = await CustomerCRUD(CustomerModel).delete_data(id, delivery_collection)
    return response


@router.post("/add_daily_order/{id}")
async def add_daily_order(id: str, data: DailyOrderModel):
    response = await CustomerCRUD(DailyOrderModel).add_daily_order(
        id, data, delivery_collection
    )
    return response


@router.post("/add_order/{id}")
async def add_order(id: str, data: OrdersModel):
    response = await CustomerCRUD(OrdersModel).add_order(id, data, delivery_collection)
    return response


@router.put("/update_order/{id}")
async def update_order(id: str, data: UpdateOrdersModel):
    response = await CustomerCRUD(UpdateOrdersModel).update_delivery_time_order(
        id, data, delivery_collection
    )
    return response


@router.post("/add_telegram/{id}")
async def add_telegram_id(id: str, data: TelegramModel):
    response = await CustomerCRUD(CustomerModel).add_telegram(
        id, data, delivery_collection
    )
    return response


@router.get("/add_orders_by_daily_orders/")
async def add_orders_by_daily_orders():
    response = await CustomerCRUD(List[Optional[Dict]]).add_orders_by_daily_orders(
        delivery_collection
    )
    return response


@router.get("/update_all_delivery_times/")
async def update_all_delivery_times():
    response = await CustomerCRUD(CustomerModel).update_all_delivery_times(
        delivery_collection
    )
    return response


@router.get("/all_delivered_orders_for_today/")
async def all_delivered_orders_for_today():
    response = await CustomerCRUD(CustomerModel).get_all_delivered_orders_for_today(
        delivery_collection
    )
    return response


@router.get("/all_orders_for_today/")
async def all_orders_for_today():
    response = await CustomerCRUD(CustomerModel).get_all_orders_for_today(
        delivery_collection
    )
    return response


@router.get("/get_customer_by_telegram_id/{telegram_id}")
async def get_customer_by_telegram_id(telegram_id: str):
    response = await CustomerCRUD(CustomerModel).get_customer_by_telegram_id(
        telegram_id, delivery_collection
    )
    return response


@router.get("/get_id_by_customer_title/{title}")
async def get_id_by_customer_title(title: str):
    response = await CustomerCRUD(CustomerModel).get_id_by_customer_title(
        title, delivery_collection
    )
    return response
