# LAUNDRY DELIVERY APP

* Laundry have many customers with periodic daily orders. This app automatic create orders by schedule.
* Customers may get delivery and check them by telegram bot.
* Admin may check statistic of delivery by day, week, month and period.

## Instalation

* git clone
* cd ..
* update .env
* make up

## Usage

* Backend Fastapi swagger on http://localhost:8000/docs or redoc on http://localhost:8000/redoc
* Frontend VueJs on http://localhost:5173
* Database Mongo on mongodb://localhost:27017

## Telegram bot

* /start - User may register own customer by title

## Testing

* Testing app by pytest
* For testing set DEBUG=True in backend/.env for switch database from laundry to laundry_test