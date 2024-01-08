import requests
import json
import os


with open(os.path.join(os.path.dirname(__file__), "daily_order_sheet.json")) as f:
    data = json.load(f)
    for i in data[:-1]:
        r = requests.post("http://localhost:8000/api/v1/delivery", json=i)
        print(r.status_code)
