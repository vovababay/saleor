from .db_connect import CONNECTION
import psycopg2.extras
from .products_sale import Products 

cur = CONNECTION.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

class Categories:
    @staticmethod
    def get_categories(sale_id: int) -> list:
        """
        Возвращает все категории со скидкой.
        """

        fetch = f"SELECT * FROM public.discount_sale_categories where sale_id = {sale_id};"
        cur.execute(fetch)
        return cur.fetchall()

    @staticmethod
    def get_category_products(category_id:int) -> list:
        """
        Возвращает список продуктов по одной коллекции.
        """
        fetch = f"SELECT * FROM public.product_product where category_id = {category_id};"
        cur.execute(fetch)
        return cur.fetchall()
    
    @staticmethod
    def get_categories_products(sale_id: int) -> list:
        """
        Возвращает список продуктов по всем категориям.
        """
        categories = Categories.get_categories(sale_id=sale_id)
        all_products = list()
        for category in categories:
            product_data = Categories.get_category_products(category.get("category_id", None))
            all_products += product_data
        return all_products
