from django.db import models
from datetime import datetime, timedelta

# Create your models here.
class JsonFileForParser(models.Model):
    file = models.FileField(
        upload_to="uploads/%Y/%m/%d/", blank=True, null=True, verbose_name="Файл"
    )


class NumberPaymentOrder(models.Model):
    number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Номер заказа")
    token = models.CharField(null=True, max_length=255, blank=True, verbose_name="Токен заказа")
    payment_id = models.CharField(null=True, max_length=255, blank=True, verbose_name="Номер платежа")
    hash_token = models.CharField(null=True, max_length=255, blank=True, verbose_name="Токен платежа")
    date_close = models.DateTimeField(blank=True, null=True, verbose_name="Когда закончить проверку оплаты")
