import os
from typing import Optional, List

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from source.config import MONGODB_URL

from typing_extensions import Annotated

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument
from source.laundry.router import router as laundry_router


app = FastAPI(
    title="Delivery API",
    summary="A simple API to manage delivery",
)

api_v1_routers = [
    laundry_router
]

for router in api_v1_routers:
    app.include_router(router, prefix="/api/v1")
    