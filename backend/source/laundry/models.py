from bson import ObjectId
from datetime import datetime, timedelta
from source.repository import CRUDMongo
from motor.motor_asyncio import AsyncIOMotorCollection
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
        if (
            updated_data := await collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"orders": data.model_dump(by_alias=True)}},
            )
        ).modified_count == 1:
            if (
                updated_data := await collection.find_one({"_id": ObjectId(id)})
            ) is not None:
                return CustomerModel.model_validate(updated_data)
        return None

    async def add_telegram(
        self, id: str, data: TelegramModel, collection: AsyncIOMotorCollection
    ) -> CustomerModel:
        """
        Add a telegram to a customer.
        """
        if (
            updated_data := await collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"telegram": data.model_dump(by_alias=True)}},
            )
        ).modified_count == 1:
            if (
                updated_data := await collection.find_one({"_id": ObjectId(id)})
            ) is not None:
                return CustomerModel.model_validate(updated_data)
        return None

    async def add_orders_by_daily_orders(self, collection: AsyncIOMotorCollection):
        """
        get today_daily_orders
        for each daily_order in today_daily_orders:
            create order for each customer with that daily_order
        """
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
                        second=int(daily_order["time_of_day"][6:]),
                    )
                    order = OrdersModel(
                        order_day_time=order_day_time, delivery_day_time=None
                    )
                    await self.add_order(customer["_id"], order, collection)
        return True

    async def update_all_delivery_times(
        self, collection: AsyncIOMotorCollection
    ) -> list[dict]:
        modified_orders = []
        cursor = collection.find({"orders.delivery_day_time": None})
        async for document in cursor:
            customer_name = document.get("title", "Unknown Customer")
            orders = document.get("orders", [])
            for order in orders:
                if order.get("delivery_day_time") is None:
                    order["delivery_day_time"] = order.get("order_day_time")
                    modified_orders.append(
                        {"customer_name": customer_name, "order": order}
                    )

            await collection.update_one(
                {"_id": document["_id"]}, {"$set": {"orders": orders}}
            )

        return modified_orders

    async def get_all_overdue_orders_for_today(
        self, collection: AsyncIOMotorCollection
    ) -> list[dict]:
        overdue_orders = []
        today = datetime.now()
        cursor = collection.find({"orders.delivery_day_time": {"$lt": today}})
        async for document in cursor:
            customer_name = document.get("title", "Unknown Customer")
            orders = document.get("orders", [])
            for order in orders:
                if order.get("delivery_day_time") is not None:
                    if order.get("delivery_day_time") > order.get("order_day_time"):
                        overdue_seconds = (
                            order.get("delivery_day_time") - order.get("order_day_time")
                        ).total_seconds()
                        order["overdue"] = str(timedelta(seconds=overdue_seconds))
                        overdue_orders.append(
                            {"customer_name": customer_name, "order": order}
                        )
        return overdue_orders

    async def get_all_delivered_orders_for_today(
        self, collection: AsyncIOMotorCollection
    ) -> list[dict]:
        delivered_orders = []
        today = datetime.now()
        cursor = collection.find({"orders.delivery_day_time": {"$lt": today}})
        async for document in cursor:
            customer_name = document.get("title", "Unknown Customer")
            orders = document.get("orders", [])
            for order in orders:
                if order.get("delivery_day_time") is not None:
                    if order.get("delivery_day_time") > order.get("order_day_time"):
                        overdue_seconds = (
                            order.get("delivery_day_time") - order.get("order_day_time")
                        ).total_seconds()
                        order["overdue"] = str(timedelta(seconds=overdue_seconds))
                    else:   
                        overdue_seconds = (
                            order.get("order_day_time") - order.get("delivery_day_time")
                        ).total_seconds()
                        order["early"] = str(timedelta(seconds=overdue_seconds))
                    delivered_orders.append(
                        {"customer_name": customer_name, "order": order}
                    )
        return delivered_orders