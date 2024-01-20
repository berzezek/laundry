from dotenv import load_dotenv
import os

load_dotenv()

TIMEZONE = os.getenv("TIMEZONE")

DELIVERY_SERVICE_API_URL = os.getenv("DELIVERY_SERVICE_API_URL")

SHEDULE_ADD_ORDERS, SCHEDULE_UPDATE_ORDERS = os.getenv("SCHEDULE_TIME").split(',')