from requests import get, post, put, delete, HTTPError
from datetime import datetime


def test_api():
    """
    An automated version of the manual testing I've been doing,
    testing the lifecycle of an inserted document.
    """
    delivery_root = "http://localhost:8000/api/v1/delivery/"

    initial_doc = {
        "title": "Test Title",
        "is_active": True,
        "description": "tt",
    }

    try:
        # Insert a customer doc
        response = post(delivery_root, json=initial_doc)
        response.raise_for_status()
        doc = response.json()
        inserted_id = doc["_id"]
        print(f"Inserted document with id: {inserted_id}")
        print(
            "If the test fails in the middle you may want to manually remove the document."
        )
        assert doc["title"] == "Test Title"
        assert doc["description"] == "tt"
        assert doc["is_active"] is True
        assert doc["daily_orders"] == []
        assert doc["orders"] == []
        assert doc["telegram"] == []

        # List customers and ensure it's present
        response = get(delivery_root)
        response.raise_for_status()
        customer_ids = {s["_id"] for s in response.json()["customers"]}
        assert inserted_id in customer_ids

        # Get individual customer doc
        response = get(delivery_root + inserted_id)
        response.raise_for_status()
        doc = response.json()
        assert doc["_id"] == inserted_id
        assert doc["title"] == "Test Title"
        assert doc["is_active"] is True
        assert doc["daily_orders"] == []
        assert doc["orders"] == []
        assert doc["telegram"] == []

        # Update the customer doc
        response = put(
            delivery_root + inserted_id,
            json={
                "title": "Updated Title",
            },
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["title"] == "Updated Title"
        assert doc["description"] == "tt"
        assert doc["is_active"] is True
        assert doc["daily_orders"] == []
        assert doc["orders"] == []
        assert doc["telegram"] == []

        # Get the customer doc and check for change
        response = get(delivery_root + inserted_id)
        response.raise_for_status()
        doc = response.json()
        assert doc["_id"] == inserted_id
        assert doc["title"] == "Updated Title"
        assert doc["description"] == "tt"
        assert doc["is_active"] is True
        assert doc["daily_orders"] == []
        assert doc["orders"] == []
        assert doc["telegram"] == []

        # Insert a daily order doc
        response = post(
            delivery_root + "add_daily_order/" + inserted_id,
            json={"day_of_week": 1, "is_active": True, "time_of_day": "10:00:00"},
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["daily_orders"] == [
            {"day_of_week": 1, "is_active": True, "time_of_day": "10:00:00"}
        ]

        # Insert duplicate daily order doc
        response = post(
            delivery_root + "add_daily_order/" + inserted_id,
            json={"day_of_week": 1, "is_active": True, "time_of_day": "10:00:00"},
        )
        assert response.status_code == 400

        # Insert one more daily order doc
        today_weekday = datetime.now().weekday()
        response = post(
            delivery_root + "add_daily_order/" + inserted_id,
            json={
                "day_of_week": today_weekday,
                "is_active": True,
                "time_of_day": "10:20:00",
            },
        )
        response.raise_for_status()
        doc = response.json()
        assert len(doc["daily_orders"]) == 2

        # Insert order doc
        response = post(
            delivery_root + "add_order/" + inserted_id,
            json={"order_day_time": "2021-10-10 10:00:00"},
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["orders"][0]["order_day_time"] == "2021-10-10T10:00:00"
        assert doc["orders"][0]["delivery_day_time"] == None

        # Update order doc
        response = put(
            delivery_root + "update_order/" + inserted_id,
            json={
                "order_day_time": "2021-10-10 10:00:00",
                "delivery_day_time": "2021-10-10 10:30:00",
            },
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["orders"][0]["order_day_time"] == "2021-10-10T10:00:00"
        assert doc["orders"][0]["delivery_day_time"] == "2021-10-10T10:30:00"

        # Update order doc with another order
        response = put(
            delivery_root + "update_order/" + inserted_id,
            json={
                "order_day_time": "2021-10-10 10:00:00",
                "delivery_day_time": "2021-10-10 10:40:00",
            },
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["orders"][0]["order_day_time"] == "2021-10-10T10:00:00"
        assert doc["orders"][0]["delivery_day_time"] == "2021-10-10T10:40:00"

        # Insert telegram doc
        response = post(
            delivery_root + "add_telegram/" + inserted_id,
            json={"telegram_id": 123456789, "telegram_name": "Test Name"},
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["telegram"] == [
            {"telegram_id": 123456789, "telegram_name": "Test Name", "is_active": True}
        ]

        # Set orders by daily orders
        response = get(delivery_root + "add_orders_by_daily_orders/")
        response.raise_for_status()
        today = datetime.now()
        doc = response.json()
        assert len(doc) == 1
        assert (
            doc[0]["order_day_time"]
            == today.replace(hour=10, minute=20, second=0, microsecond=0).isoformat()
        )

        # Delete the docNone
        # Get the doc and ensure it's been deleted
        response = get(delivery_root + inserted_id)
        assert response.status_code == 200
    except HTTPError as he:
        print(he.response.json())
        raise
