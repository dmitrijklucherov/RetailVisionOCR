import psycopg2


def generate_messy_db():
    connection = psycopg2.connect(
        dbname="postgres", user="postgres", password="flashka57rus", host="127.0.0.1", port="5432"
    )
    cursor = connection.cursor()

    for i in range(1, 101):
        if i % 3 == 0:
            p_type, title, price, status = "Смартфон", f"  iPhone Модель {i} ", f" {80000 + i * 100} руб. ", "success"
        elif i % 3 == 1:
            p_type, title, price, status = "Наушники", f" AirPods-{i}   ", f"   {15000 + i * 10} ", "success"
        else:
            p_type, title, price, status = "Чехол", f"  Чехол-Книжка {i} ", f" {300 + i} руб. ", "failed"

        cursor.execute(
            "INSERT INTO messy_marketplace_stock (product_type, title, raw_price, item_status) VALUES (%s, %s, %s, %s);",
            (p_type, title, price, status)
        )
    connection.commit()
    cursor.close()
    connection.close()
    print("--- БАЗА НА 100 ГРЯЗНЫХ СТРОК УСПЕШНО СГЕНЕРИРОВАНА В POSTGRESQL! ---")


generate_messy_db()

