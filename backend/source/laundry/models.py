import re
from bson import ObjectId
from typing import Optional
from datetime import datetime, timedelta
from source.repository import CRUDMongo
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from fastapi import HTTPException
from source.laundry.schemas import (
    CustomerModel,
    CustomerCollection,
    UpdateCustomerModel,
    DailyOrderModel,
    OrdersModel,
    UpdateOrdersModel,
    TelegramModel,
)


class CustomerCRUD(CRUDMongo[CustomerModel, CustomerCollection, UpdateCustomerModel]):
    async def add_daily_order(
        self, id: str, data: DailyOrderModel, collection: AsyncIOMotorCollection
    ) -> CustomerModel:
        """
        Add a daily order to a customer.
        Ensure that daily_orders are unique by day_of_week and time_of_day.
        """
        # Check for uniqueness of the daily_order based on day_of_week and time_of_day
        existing_order = await collection.find_one(
            {
                "_id": ObjectId(id),
                "daily_orders": {
                    "$elemMatch": {
                        "day_of_week": data.day_of_week,
                        "time_of_day": data.time_of_day,
                    }
                },
            }
        )
        if existing_order:
            # If such an order already exists, return the current customer data
            raise HTTPException(
                status_code=400,
                detail=f"Daily order for day_of_week {data.day_of_week} and time_of_day {data.time_of_day} already exists",
            )

        # Add the new daily_order
        if (
            updated_data := await collection.update_one(
                {"_id": ObjectId(id)},
                {"$push": {"daily_orders": data.model_dump(by_alias=True)}},
            )
        ).modified_count == 1:
            if (
                updated_data := await collection.find_one({"_id": ObjectId(id)})
            ) is not None:
                return CustomerModel.model_validate(updated_data)
        return None

    async def add_order(
        self, id: str, data: OrdersModel, collection: AsyncIOMotorCollection
    ) -> CustomerModel:
        """
        Add a order to a customer.
        """
        if (
            updated_data := await collection.update_one(
                {"_id": ObjectId(id)},
                {"$push": {"orders": data.model_dump(by_alias=True)}},
            )
        ).modified_count == 1:
            if (
                updated_data := await collection.find_one({"_id": ObjectId(id)})
            ) is not None:
                return CustomerModel.model_validate(updated_data)
        return None

    async def update_delivery_time_order(
        self, id: str, data: UpdateOrdersModel, collection: AsyncIOMotorCollection
    ) -> CustomerModel:
        """
        Update a order to a customer.
        """
        data = {
            k: v for k, v in data.model_dump(by_alias=True).items() if v is not None
        }
        if len(data) >= 1:
            update_result = await collection.find_one_and_update(
                {"_id": ObjectId(id), "orders.order_day_time": data["order_day_time"]},
                {
                    "$set": {
                        "orders.$.delivery_day_time": data["delivery_day_time"],
                        "orders.$.delivered_by": data["delivered_by"],
                    }
                },
                return_document=ReturnDocument.AFTER,
            )
            if update_result is not None:
                return CustomerModel.model_validate(update_result)
            else:
                raise HTTPException(status_code=404, detail=f"Data {id} not found")

        # The update is empty, but we should still return the matching document:
        if (existing_data := await collection.find_one({"_id": id})) is not None:
            return self.model.model_validate(existing_data)

        raise HTTPException(status_code=404, detail=f"Data {id} not found")

    async def add_telegram(
        self, id: str, data: TelegramModel, collection: AsyncIOMotorCollection
    ) -> CustomerModel:
        """
        Add a telegram to a customer if it doesn't already exist.
        """
        # Check if the same Telegram already exists in the collection for this user
        existing_data = await collection.find_one(
            {"_id": ObjectId(id), "telegram": {"$in": [data.model_dump(by_alias=True)]}}
        )
        # If the data already exists, return the existing CustomerModel object
        if existing_data:
            return CustomerModel.model_validate(existing_data)

        # If such data does not exist, add it
        if (
            updated_data := await collection.update_one(
                {"_id": ObjectId(id)},
                {"$push": {"telegram": data.model_dump(by_alias=True)}},
            )
        ).modified_count == 1:
            if (
                updated_data := await collection.find_one({"_id": ObjectId(id)})
            ) is not None:
                return CustomerModel.model_validate(updated_data)

        return None

    async def add_orders_by_daily_orders(
        self, collection: AsyncIOMotorCollection
    ) -> list[Optional[dict]]:
        """
        get today_daily_orders
        for each daily_order in today_daily_orders:
            create order for each customer with that daily_order
        """
        adding_orders = []
        weekday_number = datetime.now().weekday()
        today_daily_orders = await collection.find(
            {
                "is_active": True,
                "daily_orders": {"$elemMatch": {"day_of_week": weekday_number}},
            }
        ).to_list(1000)

        for customer in today_daily_orders:
            for daily_order in customer["daily_orders"]:
                if daily_order["day_of_week"] == weekday_number:
                    order_day_time = datetime.now().replace(
                        hour=int(daily_order["time_of_day"][:2]),
                        minute=int(daily_order["time_of_day"][3:5]),
                        second=0,
                        microsecond=0,
                    )
                    order = OrdersModel(order_day_time=order_day_time)
                    await self.add_order(customer["_id"], order, collection)
                    adding_orders.append(
                        {
                            "customer_name": customer["title"],
                            "order_day_time": order_day_time,
                        }
                    )
        return adding_orders

    async def update_all_delivery_times(
        self, collection: AsyncIOMotorCollection
    ) -> list[Optional[dict]]:
        """
        get today_orders
        for each order in today_orders:
            if delivery_day_time is None:
                update delivery_day_time to order_day_time
                update delivered_by to 'По расписанию'
        """
        today_orders = await self.get_all_orders_for_today(collection)
        updated_orders = []
        for orders in today_orders:
            for order in orders["today_orders"]:
                if order["delivery_day_time"] == None:
                    delivery_day_time = order["order_day_time"]
                    delivered_by = "По расписанию"
                    await collection.find_one_and_update(
                        {
                            "title": orders["title"],
                            "orders.order_day_time": order["order_day_time"],
                        },
                        {
                            "$set": {
                                "orders.$.delivery_day_time": delivery_day_time,
                                "orders.$.delivered_by": delivered_by,
                            }
                        })
                    updated_orders.append(
                        {
                            "customer_name": orders["title"],
                            "order_day_time": order["order_day_time"],
                            "delivery_day_time": delivery_day_time,
                            "delivered_by": delivered_by,
                        }
                    )
        return updated_orders

    async def get_all_delivered_orders_for_today(
        self, collection: AsyncIOMotorCollection
    ) -> list[dict]:
        current_date_str = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        pipeline = [
            {"$unwind": "$orders"},
            {
                "$match": {
                    "orders.order_day_time": {"$gte": current_date_str},
                    "orders.delivery_day_time": {"$ne": None},
                }
            },
            {
                "$group": {
                    "_id": "$title",
                    "orders": {
                        "$push": {
                            "order_day_time": "$orders.order_day_time",
                            "delivery_day_time": "$orders.delivery_day_time",
                        }
                    },
                }
            },
            {
                "$project": {
                    "title": "$_id",
                    "_id": 0,
                    "today_delivered_orders": "$orders",
                }
            },
        ]

        today_delivered_orders = []
        async for orders in collection.aggregate(pipeline):
            today_delivered_orders.append(orders)

        return today_delivered_orders

    async def get_all_orders_for_today(
        self, collection: AsyncIOMotorCollection
    ) -> list[dict]:
        current_date_str = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        pipeline = [
            {"$unwind": "$orders"},
            {"$match": {"orders.order_day_time": {"$gte": current_date_str}}},
            {
                "$group": {
                    "_id": "$title",
                    "orders": {
                        "$push": {
                            "order_day_time": "$orders.order_day_time",
                            "delivery_day_time": "$orders.delivery_day_time",
                            "delivered_by": "$orders.delivered_by",
                        }
                    },
                }
            },
            {"$project": {"title": "$_id", "_id": 0, "today_orders": "$orders"}},
        ]

        today_orders = []
        async for orders in collection.aggregate(pipeline):
            today_orders.append(orders)

        return today_orders

    async def get_customer_by_telegram_id(
        self, telegram_id: str, collection: AsyncIOMotorCollection
    ) -> CustomerModel:
        if (
            customer := await collection.find_one({"telegram.telegram_id": telegram_id})
        ) is not None:
            return CustomerModel.model_validate(customer)
        return None

    async def get_id_by_customer_title(
        self, title: str, collection: AsyncIOMotorCollection
    ) -> str:
        regex_pattern = re.compile(f"^{re.escape(title)}$", re.IGNORECASE)
        if (
            customer := await collection.find_one({"title": {"$regex": regex_pattern}})
        ) is not None:
            return str(customer["_id"])
        return None
        return None

    async def get_id_by_customer_description(
        self, description: str, collection: AsyncIOMotorCollection
    ) -> str:
        regex_pattern = re.compile(f"^{re.escape(description)}$", re.IGNORECASE)
        if (
            customer := await collection.find_one(
                {"description": {"$regex": regex_pattern}}
            )
        ) is not None:
            return str(customer["_id"])
        return None
