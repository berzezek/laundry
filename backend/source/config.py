from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

DEBUG = os.getenv("DEBUG")

MONGODB = "delivery"

DELIVERY_SERVICE_API_URL = os.getenv("DELIVERY_SERVICE_API_URL")
