from datetime import datetime
import pytz

from .db_connect import CONNECTION
import psycopg2.extras

utc=pytz.UTC
cur = CONNECTION.cursor(cursor_factory = psycopg2.extras.RealDictCursor)


class Sales:

    @staticmethod
    def get_date_now():
        """
        Возвращает текущию дату и время.
        """
        return datetime.now()

    @staticmethod
    def get_sales():
        """
        Возвращает все скидки с переодически изменяющейся ценой.
        Фильтрует по дате (дата начала скидки <= текущая дата <= дата окончания скидки)
        """
        date_now = utc.localize(Sales.get_date_now())
        fetch = f"SELECT * FROM public.discount_sale where periodically_change='true' and "\
        f"start_date <= '{date_now}' and (end_date is null or end_date >= '{date_now}');"
        cur.execute(fetch)
        return cur.fetchall()

    @staticmethod
    def get_sales_id() -> list:
        sales_ids = list()
        sales = Sales.get_sales()
        for sale in sales:
            sales_ids.append(sale.get("id", None))
        return sales_ids
