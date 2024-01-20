import requests
from config import DELIVERY_SERVICE_API_URL


def add_orders_by_dayly_orders():
    requests.get(DELIVERY_SERVICE_API_URL + "add_orders_by_daily_orders/")
    
def update_all_delivery_times():
    requests.get(DELIVERY_SERVICE_API_URL + "update_all_delivery_times/")