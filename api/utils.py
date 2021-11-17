from typing import List
import requests
from hashlib import sha256
import collections
from fake_useragent import UserAgent
from urllib import request, parse
import json
from .models import NumberPaymentOrder
from sale_reduction.db_connect import CONNECTION
import psycopg2.extras
from datetime import datetime, timedelta
from saleor.order.models import Order, Fulfillment
from saleor.payment.models import Payment
cur = CONNECTION.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

PASSWORD = "sutabsonpgp7q2xm"
TERMINAL_KEY = "1633428465142"


def create_hash_token(PaymentId, number):
    text_data = ""
    global PASSWORD
    text_data += PASSWORD
    text_data += PaymentId
    text_data += TERMINAL_KEY

    result = sha256(text_data.encode("utf-8")).hexdigest()
    number.hash_token = result
    number.save()
    return result


def get_state(payment_id, hash_token):
    #AUTH_FAIL
    #AUTHORIZED
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json" ,
        'User-Agent': "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1"
    }
    )
    data_req={
     "TerminalKey": TERMINAL_KEY,
     "PaymentId": payment_id,
     "Token" : hash_token.lower()
    }
    json_object = json.dumps(data_req)
    r = session.post(url="https://securepay.tinkoff.ru/v2/GetState/", data=json_object)
    return r.json().get("Status")


def get_all_payments_tinkoff():
    """
    Возвращает все платежные транзакции.
    """
    payments = NumberPaymentOrder.objects.filter(date_close__gte=datetime.now())
    print(payments)
    for payment in payments:
        order = Order.objects.get(checkout_token=payment.token)
        payment_data = Payment.objects.get(order=order)
        payment_status = get_state(payment.payment_id, payment.hash_token)
        print(payment_status)
        if payment_status == "AUTHORIZED":
            payment_data.charge_status = "fully-charged"
            payment_data.save()
        else:
            payment_data.charge_status = "not-charged"
            payment_data.save()
def create_data_req(data: dict, order_id: int) -> dict:
    data_req = {
        "TerminalKey": TERMINAL_KEY,
        "OrderId": order_id,
        "Description": data.get("description", "none"),
        "NotificationURL": "http://0.0.0.0:3000/checkout/shipping",
        "SuccessURL":"http://0.0.0.0:3000/checkout/shipping",
        "FailURL":"http://0.0.0.0:3000/checkout/shipping",
        "Receipt": {
            "EmailCompany": "vadim_gkm@mail.ru",
            "Taxation": "osn",
        },
    }
    email = data.get("email")
    phone = data.get("phone")
    if email:
        data_req["Receipt"]["Email"] = email
    if phone:
        data_req["Receipt"]["Phone"] = phone

    items = []
    all_amount = 0

    for product in data.get("products"):
        amount = product.get("amount")
        if amount:
            amount = amount * 100
        item_data = dict()

        item_data["Name"] = product.get("name", "none")
        item_data["Quantity"] = product.get("quantity", "none")
        item_data["Price"] = amount
        item_amount = amount * int(product.get("quantity"))
        item_data["Amount"] = item_amount
        item_data["PaymentMethod"] = "full_prepayment"
        item_data["PaymentObject"] = "commodity"
        item_data["Tax"] = "none"
        items.append(item_data)
        all_amount += int(item_amount)
    data_req["Amount"] = int(all_amount)

    data_req["Receipt"]["Items"] = items
    return data_req


def get_url_payment(data_req, number):
    json_object = json.dumps(data_req)
    req = requests.post(url="https://securepay.tinkoff.ru/v2/Init", data=json_object, headers={"content-type": "application/json"})
    print()

    number.payment_id=req.json().get("PaymentId")
    number.save()
    return req.json()
