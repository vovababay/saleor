from .db_connect import CONNECTION
import psycopg2.extras


cur = CONNECTION.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

class Products:
    @staticmethod
    def get_product(product_id):
        """
        Возвращает продукт.
        """
        fetch = f"SELECT * FROM public.product_product where id = {product_id};"
        cur.execute(fetch)
        return cur.fetchall()

    @staticmethod
    def get_sale_products(sale_id):
        """
        Возвращает продукты с скидкой.
        """
        all_products = list()
        fetch = f"SELECT * FROM public.discount_sale_products where sale_id = {sale_id};"
        cur.execute(fetch)
        products = cur.fetchall()
        for product in products:
            product_data = Products.get_product(product.get("product_id", None))
            all_products += product_data
        return all_products

    @staticmethod
    def get_variants_product(product_id):
        """
        Возвращает варианты продукта
        """
        #product_productvariant
        fetch = f"SELECT * FROM public.product_productvariant where product_id = {product_id};"
        cur.execute(fetch)
        variants = cur.fetchall()

        return variants
