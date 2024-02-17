from aiogram import F, Router
from aiogram.types import CallbackQuery, InputFile
from keyboards.simple_fab import OrdersCallbackFactory
from datetime import datetime
import pandas as pd
from openpyxl.utils import get_column_letter
from bot import logging
from keyboards.simple_fab import get_admin_keyboard_fab
from utils import get_all_orders_for_today, get_all_delivered_orders_for_today, get_all_customers, format_orders
from config import BASE_DIR

router = Router()


# @router.callback_query(OrdersCallbackFactory.filter(F.action == "add_customer"))
# async def callbacks_delivery_allready_delivered(
#     callback: CallbackQuery, callback_data: OrdersCallbackFactory
# ):
#     await callback.answer("Добавить Заказчика")


@router.callback_query(OrdersCallbackFactory.filter(F.action == "get_statistic"))
async def callbacks_delivery_allready_delivered(
    callback: CallbackQuery, callback_data: OrdersCallbackFactory
):
    data = get_all_orders_for_today()
    # Формируем заголовок таблицы
    message = f"Статистика за {datetime.now().strftime('%d.%m.%Y')}\n\n"

    # Добавляем строки таблицы
    for item in data.json():
        if item['today_orders'] == []:
            continue
        customer_name = item['title']
        message += f"{customer_name}\n"
        for order in item['today_orders']:
            order_hour_minute = order['order_day_time'].split("T")[1].split(".")[0][:-3]
            if order['delivery_day_time']:
                delivery_hour_minute = order['delivery_day_time'].split("T")[1].split(".")[0][:-3]
            else:
                delivery_hour_minute = "Не доставлено"
            message += f"\t{order_hour_minute} | {delivery_hour_minute} {'| ' + str(order['delivered_by']) if order['delivered_by'] else ''}\n"
        message += "---\n"
    # Отправляем сообщение
    await callback.message.answer(text=f"```\n{message}\n```", parse_mode="Markdown", reply_markup=get_admin_keyboard_fab())


@router.callback_query(OrdersCallbackFactory.filter(F.action == "download_statistic"))
async def callbacks_delivery_allready_delivered(
    callback: CallbackQuery, callback_data: OrdersCallbackFactory
):
    data = get_all_orders_for_today()

    data = data.json()
    rows = []
    for entry in data:
        rows.append({"Наименование": entry['title']})  # Добавляем наименование
        for order in entry['today_orders']:
            order_time = datetime.fromisoformat(order['order_day_time'])
            delivery_time = datetime.fromisoformat(order['delivery_day_time'])
            delay = delivery_time - order_time
            note = "Опоздание" if delay.total_seconds() > 0 else "Вовремя"
            rows.append({
                "Наименование": "",
                "Доставка на сегодня": order_time.strftime("%H:%M"),
                "Время доставки": delivery_time.strftime("%H:%M"),
                "Примечание": f"{note} {abs(delay.seconds)//3600:02}:{(abs(delay.seconds)//60)%60:02}"
            })
        rows.append({})  # Добавляем пустую строку между объектами

    df = pd.DataFrame(rows)

    # Создание Excel файла
    filename = f"{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    file_path = f"{BASE_DIR}/aiogram/static/reports/daily_reports/{filename}"
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    df.to_excel(writer, index=False)

    # Установка ширины столбцов
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets['Sheet1'].column_dimensions[get_column_letter(col_idx + 1)].width = column_width

    writer._save()
    writer.close()

    await callback.answer(f"Отчет {filename} сформирован")
    await callback.answer.send_document(InputFile(file_path), caption=f"Отчет {filename}")



    
@router.callback_query(OrdersCallbackFactory.filter(F.action == "periodic_orders"))
async def callbacks_delivery_allready_delivered(
    callback: CallbackQuery, callback_data: OrdersCallbackFactory
):
    data = get_all_customers()

    message = "|    Таблица периодических заказов\n|\n"

    # Перебор каждого заказчика и добавление информации в сообщение
    for customer in data.json()["customers"]:
        message += f"| **{customer['title']} ({customer['description']})**\n"
        order_lines = format_orders(customer["daily_orders"])
        message += "|  Пн   |  Вт   |  Ср   |  Чт   |  Пт   |  Сб   |  Вс   |\n"
        message += "|-------|-------|-------|-------|-------|-------|-------|\n"
        for line in order_lines:
            message += line + "\n"
            
    await callback.message.answer(text=f"```\n{message}\n```", parse_mode="Markdown", reply_markup=get_admin_keyboard_fab())
