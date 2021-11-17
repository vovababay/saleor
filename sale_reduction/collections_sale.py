from .db_connect import CONNECTION
import psycopg2.extras
from .products_sale import Products 

cur = CONNECTION.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

class Collections:
    """
    ЧТо то делает
    """
    @staticmethod
    def get_collections(sale_id: int) -> list:
        """
        Возвращает все коллекций со скидкой.
        """

        fetch = f"SELECT * FROM public.discount_sale_collections where sale_id = {sale_id};"
        cur.execute(fetch)
        return cur.fetchall()
    @staticmethod
    def get_collection_products(collection_id:int) -> list:
        """
        Возвращает список продуктов по одной коллекции.
        """
        fetch = f"SELECT * FROM public.product_collectionproduct where collection_id = {collection_id};"
        cur.execute(fetch)
        return cur.fetchall()
    


    @staticmethod
    def get_collections_products(sale_id: int) -> list:
        """
        Возвращает список продуктов по всем коллекциям.
        """
        collections = Collections.get_collections(sale_id=sale_id)
        all_products = list()
        for collection in collections:
            collection_data = Collections.get_collection_products(collection.get("collection_id", None))
            for product_collection in collection_data:
                product = Products.get_product(product_collection.get("product_id", None))
                all_products += product
        return all_products
