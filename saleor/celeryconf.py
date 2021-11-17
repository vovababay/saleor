import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

from .plugins import discover_plugins_modules

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saleor.settings")

app = Celery("saleor")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.autodiscover_tasks(lambda: discover_plugins_modules(settings.PLUGINS))
app.conf.beat_schedule = {
    'rediction-price-every-1-minute':
        {
            'task': 'rediction_price',
            'schedule': crontab(),#crontab(minute=0, hour=2),
        },
    "generate_xml_announcement": {
            "task": "saleor.product.tasks.generate_xml",
            "schedule": crontab(),#crontab(minute=1, hour=0),
        },
    "update_status_payment": {
        "task": "api.tasks.update_status_payment",
        "schedule": crontab(),  # crontab(minute=1, hour=0),
        }
    }
