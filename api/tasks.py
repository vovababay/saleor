from saleor.celeryconf import app
from .utils import get_all_payments_tinkoff


@app.task(bind=True)
def update_status_payment(*args, **kwargs):
    get_all_payments_tinkoff()




