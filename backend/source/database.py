import os
import motor.motor_asyncio
from source.config import MONGODB_URL, MONGODB


client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.college
delivery_collection = db.get_collection(MONGODB)
