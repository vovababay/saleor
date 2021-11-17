from typing import Iterable, List, Optional

from ..celeryconf import app
from ..discount.models import Sale
from .models import Attribute, Product, ProductType, ProductVariant
from .utils.attributes import generate_name_for_variant
from .utils.variant_prices import (
    update_product_minimal_variant_price,
    update_products_minimal_variant_prices,
    update_products_minimal_variant_prices_of_catalogues,
    update_products_minimal_variant_prices_of_discount,
)
from datetime import datetime, timedelta
from saleor.settings import MEDIA_ROOT


@app.task(bind=True)
def generate_xml(self):
    # updated_at
    new_date = (datetime.now() - timedelta(days=1)).date()
    now_date = datetime.now().date()
    first_datetime = datetime(new_date.year, new_date.month, new_date.day, 0, 0, 0)
    last_datetime = datetime(now_date.year, now_date.month, now_date.day, 0, 0, 0)
    all_products = (
        Product.objects.all()
    )  # (Q(updated_at = datetime(new_date.year, new_date.month, new_date.day)))

    # print(all_products, "!!!!!!!!!!!!!!!!!!!")
    # <?xml version="1.0"?>
    new_products = []
    for product in all_products:
        bool_date_one = (product.updated_at.date() >= first_datetime.date()) and (
            product.updated_at.time() >= first_datetime.time()
        )
        bool_date_two = product.updated_at.date() <= last_datetime.date()
        if bool_date_one and bool_date_two:
            new_products.append(product)
        # if ((product.updated_at.date() > first_datetime.date()) and (product.updated_at.time() > first_datetime.time())) or (product.updated_at < last_datetime):
        #    is_update = True
    # if is_update == True:
    file = open(f"{MEDIA_ROOT}/parse_products.xml", mode="w+t", encoding="utf-8")
    file.write('<?xml version="1.0"?>\n')
    file.write('<Ads formatVersion = "3" target = "Avito.ru">\n')
    for product in new_products:
        # if (product.update_at > firt_datetime) or (product.update_at < last_datetime):
        # print(product.updated_at)
        file.write(f"<Ad><Id>{product.id}</Id>\n")
        file.write(
            f"<DateBegin>{datetime.now()}</DateBegin>\n"
        )  # Возможно тут нужно поставить сегоднешний день и дата через месяц
        file.write(f"<DateEnd>{datetime.now()+ timedelta(weeks=4)}</DateEnd>\n")
        file.write("<AdStatus>TurboSale</AdStatus>\n")
        # file.write("<AllowEmail>v_babaev@webjox.ru</AllowEmail>\n")
        # file.write("<ManagerName>Владимир</ManagerName>\n")
        file.write("<Description>Важно!\nТовар бывший в употреблении. Его пожертвовал человек, большая часть средств от продажи будет перечислена на благотворительные нужды. Состояние товара Вы можете оценить по фото, или приехать к нам в офис чтобы ознакомиться с ним лично. При оплате товара на сайте происходит заморозка средств на Вашей карте, и товар бронируется за Вами как покупателем. У Вас есть 3 календарных дня приехать в наш офис забрать заказ, иначе средства вернутся на Ваш счет, а товар снова будет выставлен на продажу. К сожалению, сейчас нет возможности организовать доставку товара, доступен только самовывоз.</Description>\n")
        file.write("<ContactPhone>+79998554444</ContactPhone>\n")
        file.write(
            "<locations><location><address>Россия, Москва, Тверская улица</address></location></locations>\n"
        )
        file.write("<Address>Россия, Москва, Тверская улица</Address>\n")
        # file.write("<images></images>\n")
        file.write(f"<Category>{product.category.parent.name if product.category.parent is not None else product.category.name}</Category>\n")
        file.write(f"<GoodsType>{product.category.name}</GoodsType>\n")
        file.write("<Condition>Б/у</Condition>\n")
        file.write("<AdType>Товар приобретен на продажу</AdType>\n")
        file.write("<Apparel>Другое</Apparel>\n")
        # file.write("<Size>S</Size>\n")
        file.write(f"<Title>{product.name}</Title>\n")
        file.write(
            "<contacts><contact-method>only-phone</contact-method><phone>+79084547877</phone></contacts>"
        )
        file.write(f"<Price>{int(product.minimal_variant_price_amount)}</Price>\n")
        # file.write(
        #     f"<Images><Image \"url=https://toursdominicana.ru/wp-content/uploads/2020/07/fruit-drakon.jpg\"/></Images>")
        if product.get_first_image() is not None:
            file.write(
                f'<Images>'
            )
            for image in product.images.all():
                file.write(
                    f'<Image url = "https://backend.lighted.ru/media/{image.image}"/>'
                )
            file.write(
                f'</Images>'
            )
        file.write("</Ad>\n")
    file.write("</Ads>")
    file.close()
    # url_start = "https://passport.yandex.ru/registration-validations/auth/multi_step/start"
    # link = "https://passport.yandex.com/auth"

    # headers = {
    # "accept": "application/json, text/javascript, */*; q=0.01",
    # "accept-language": "ru-RU,ru;q=0.9",
    # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    # "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
    # "sec-ch-ua-mobile": "?0",
    # "sec-fetch-dest": "empty",
    # "sec-fetch-mode": "cors",
    # "sec-fetch-site": "same-origin",
    # "x-requested-with": "XMLHttpRequest"
    # }
    # data = {
    # 'login': 'v_babaev@webjox.ru',
    # 'passwd': '2932065Asd!',
    # }

    # session = Session()

    # responce = session.post(link, headers=headers, data=data)

    # #req = session
    # #req = post(url=url_start, headers=headers, data=data)
    # print(responce.text)
    # #requests.Session()


def _update_variants_names(instance: ProductType, saved_attributes: Iterable):
    """Product variant names are created from names of assigned attributes.

    After change in attribute value name, for all product variants using this
    attributes we need to update the names.
    """
    initial_attributes = set(instance.variant_attributes.all())
    attributes_changed = initial_attributes.intersection(saved_attributes)
    if not attributes_changed:
        return
    variants_to_be_updated = ProductVariant.objects.filter(
        product__in=instance.products.all(),
        product__product_type__variant_attributes__in=attributes_changed,
    )
    variants_to_be_updated = variants_to_be_updated.prefetch_related(
        "attributes__values__translations"
    ).all()
    for variant in variants_to_be_updated:
        variant.name = generate_name_for_variant(variant)
        variant.save(update_fields=["name"])


@app.task
def update_variants_names(product_type_pk: int, saved_attributes_ids: List[int]):
    instance = ProductType.objects.get(pk=product_type_pk)
    saved_attributes = Attribute.objects.filter(pk__in=saved_attributes_ids)
    _update_variants_names(instance, saved_attributes)


@app.task
def update_product_minimal_variant_price_task(product_pk: int):
    product = Product.objects.get(pk=product_pk)
    update_product_minimal_variant_price(product)


@app.task
def update_products_minimal_variant_prices_of_catalogues_task(
    product_ids: Optional[List[int]] = None,
    category_ids: Optional[List[int]] = None,
    collection_ids: Optional[List[int]] = None,
):
    update_products_minimal_variant_prices_of_catalogues(
        product_ids, category_ids, collection_ids
    )


@app.task
def update_products_minimal_variant_prices_of_discount_task(discount_pk: int):
    discount = Sale.objects.get(pk=discount_pk)
    update_products_minimal_variant_prices_of_discount(discount)


@app.task
def update_products_minimal_variant_prices_task(product_ids: List[int]):
    products = Product.objects.filter(pk__in=product_ids)
    update_products_minimal_variant_prices(products)
