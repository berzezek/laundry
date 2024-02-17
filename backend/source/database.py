import motor.motor_asyncio
from source.config import MONGODB_URL, MONGODB, DEBUG

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
if DEBUG == "True":
    db = client.laundry_test
else:
    db = client.laundry
delivery_collection = db.get_collection(MONGODB)
