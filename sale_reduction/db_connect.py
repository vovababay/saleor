import psycopg2

CONNECTION = psycopg2.connect(
    host="localhost",
    database="saleor",
    user="postgres",
    password="123456")
