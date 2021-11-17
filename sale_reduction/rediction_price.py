from .db_connect import CONNECTION
import psycopg2.extras

conn = CONNECTION

#cursor(cursor_factory = psycopg2.extras.RealDictCursor)

class RedictionPrice:
    """
    Модуль для уменьшения цены у одного товара на сумму или процент указанну в параметре
    rediction_percentige_price(variants, value)
    rediction_fixed_price(variants, value)
    """

    def rediction_percentige_price(variants:list, value:float)->None:
        cur = conn.cursor()
        for variant in variants:
            price_create = variant.get("price_create", None)
            price_amount = variant.get("price_amount", None)
            variant_id = variant.get("id", None)
            if not price_create:
                fetch = f"UPDATE public.product_productvariant SET price_create={price_amount} WHERE id = {variant_id};"
                cur.execute(fetch)
                conn.commit()

            if price_create:
                new_price = int(price_amount) - ((price_create/100) * int(value))
                #print(new_price)
                if new_price > 0:
                    fetch = f"UPDATE public.product_productvariant SET price_amount={new_price} WHERE id = {variant_id};"
                    cur.execute(fetch)
                    conn.commit()
        #cur.close()
        #conn.close()
        print("[OK] PERCENTAGE")

    def rediction_fixed_price(variants:list, value:float)->None:
        cur = conn.cursor()
        for variant in variants:
            price_create = variant.get("price_create", None)
            price_amount = variant.get("price_amount", None)
            variant_id = variant.get("id", None)
            if not price_create:
                fetch = f"UPDATE public.product_productvariant SET price_create={price_amount} WHERE id = {variant_id};"
                cur.execute(fetch)
                conn.commit()
            if price_create:
                new_price = int(price_amount) - int(value)
                print(new_price)
                if new_price > 0:
                    fetch = f"UPDATE public.product_productvariant SET price_amount={new_price} WHERE id = {variant_id};"
                    cur.execute(fetch)
                    conn.commit()
        #cur.close()
        #conn.close()
        print("[OK] FIXED")
# price_create
# price_amount
