from pydantic import ConfigDict, BaseModel, Field
from bson import ObjectId
from typing import Optional
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from datetime import datetime


PyObjectId = Annotated[str, BeforeValidator(str)]


class DailyOrderModel(BaseModel):
    day_of_week: int = Field(...)
    time_of_day: str = Field(...)
    is_active: bool = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {"day_of_week": 1, "time_of_day": "10:00:00", "is_active": True}
        },
    )


class UpdateDailyOrderModel(BaseModel):
    day_of_week: Optional[int] = None
    time_of_day: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {"day_of_week": 1, "time_of_day": "10:00:01", "is_active": True}
        },
    )


class OrdersModel(BaseModel):
    order_day_time: datetime
    delivery_day_time: Optional[datetime] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "order_day_time": "2021-10-10 10:00:00",
                "delivery_day_time": "2021-10-10 10:00:05",
            }
        },
    )


class UpdateOrdersModel(BaseModel):
    order_day_time: Optional[datetime] = None
    delivery_day_time: Optional[datetime] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "order_day_time": "2021-10-10 10:00:00",
                "delivery_day_time": "2021-10-10 10:00:05",
            }
        },
    )


class TelegramModel(BaseModel):
    """
    Container for a single telegram record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    telegram_id: str = Field(...)
    telegram_name: str = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {"telegram_id": "123456789", "telegram_name": "My Telegram"}
        },
    )


class UpdateTelegramModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    telegram_id: Optional[str] = None
    telegram_name: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {"telegram_id": "123456789", "telegram_name": "My Telegram"}
        },
    )


class CustomerModel(BaseModel):
    """
    Container for a single customer record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    is_active: bool = Field(...)
    daily_orders: Optional[list[DailyOrderModel]] = []
    orders: Optional[list[OrdersModel]] = []
    telegram: Optional[TelegramModel] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"example": {"title": "My Customer", "is_active": True}},
    )


class UpdateCustomerModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    title: Optional[str] = None
    is_active: Optional[bool] = None
    daily_orders: Optional[list[UpdateDailyOrderModel]] = None
    orders: Optional[list[UpdateOrdersModel]] = None
    telegram: Optional[UpdateTelegramModel] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "title": "My no active Customer",
                "is_active": False,
                "daily_orders": [
                    {"day_of_week": 1, "time_of_day": "21:00:00", "is_active": True},
                    {"day_of_week": 3, "time_of_day": "10:30:00", "is_active": True},
                ],
                "orders": [
                    {
                        "order_day_time": "2021-10-10 10:00:00",
                        "delivery_day_time": "2021-10-10 10:00:05",
                    },
                    {
                        "order_day_time": "2021-10-10 21:00:00",
                        "delivery_day_time": "2021-10-10 21:00:05",
                    },
                ],
                "telegram": {
                    "telegram_id": "123456789",
                    "telegram_name": "My Telegram",
                },
            }
        },
    )


class CustomerCollection(BaseModel):
    """
    A container holding a list of `CustomerModel` instances.
    """

    customers: list[CustomerModel]
