import schedule
import asyncio
import time
import requests
from source.config import DELIVERY_SERVICE_API_URL

async def start_schedule():

    async def create_orders_by_daily_order():
        requests.get(DELIVERY_SERVICE_API_URL + f"add_orders_by_daily_orders/")
        
    schedule.every().day.at("04:00").do(create_orders_by_daily_order)

    while True:
        schedule.run_pending()
        await asyncio.sleep(3600)
    