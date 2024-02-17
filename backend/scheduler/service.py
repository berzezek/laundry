import time
from schedule import every, repeat, run_pending
from utils import add_orders_by_dayly_orders, update_all_delivery_times
from config import TIMEZONE, SHEDULE_ADD_ORDERS, SCHEDULE_UPDATE_ORDERS

# Add order by dayly orders
every().day.at("05:00", TIMEZONE).do(add_orders_by_dayly_orders)

# Close all orders where delivery time is None
every().day.at("21:00", TIMEZONE).do(update_all_delivery_times)

while True:
    run_pending()
    time.sleep(60)
