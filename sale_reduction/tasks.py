from saleor.celeryconf import app

from .collections_sale import Collections
from .categories_sale import Categories
from .products_sale import Products
from .sales import Sales
from .type_sales import *
from .rediction_price import RedictionPrice

# Получение продуктов
# collections = Collections.get_collections_products(sale_id=2)
# categories = Categories.get_categories_products(sale_id=3)
# products = Products.get_sale_products(3)


# Нужно пройтись по каждой распродаже и уменьшить цену у товаров по категориям, коллекциям и товарам

def get_products_in_sale(sale_id:int) ->list:
    """
    Получение всех продуктов в скидке из калекорий, коллекций и просто привязанных продуктов.
    """
    all_products = list()
    collections = Collections.get_collections_products(sale_id=sale_id)
    all_products += collections
    categories = Categories.get_categories_products(sale_id=sale_id)
    all_products += categories
    products = Products.get_sale_products(sale_id=sale_id)
    all_products += products
    return all_products


def get_all_variants(products:list) -> list:
    """
    Получение всех вариантов продуктов из списка продуктов.
    """
    all_variants_in_sale = list()
    for productds in products:
        all_variants_in_sale += Products.get_variants_product(productds.get("id"))
    return all_variants_in_sale


@app.task(name="rediction_price", bind=True)
def rediction_price(*args, **kwargs):
    sales = Sales.get_sales()

    for sale in sales:
        sale_id=sale.get("id", None)
        all_variants_in_sale = get_all_variants(products=get_products_in_sale(sale_id=sale_id))
        type_sale = sale.get("type", None)
        value = sale.get("value", None)

        if type_sale == PERCENTAGE:
            RedictionPrice.rediction_percentige_price(all_variants_in_sale, value)

        elif type_sale == FIXED:
            RedictionPrice.rediction_fixed_price(all_variants_in_sale, value)
