import psycopg2

# 1. СЫРЫЕ ГРЯЗНЫЕ ДАННЫЕ ОТ ПОСТАВЩИКОВ
raw_items = [
    {"name": "Наушники", "art": "  WB-101-AA ", "price": "1500 руб."},
    {"name": "Мышка", "art": "OZ- 202 - BB", "price": " 3200 "},
    {"name": "Клавиатура", "art": "WB - 303 - CC   ", "price": "25000 руб."}
]

# Очищаем и возвращаем чистые дынные
def clen_item_data(item_dict):
    clean_art = item_dict["art"].strip().replace("-","").replace(" ", "")
    raw_price = item_dict["price"].replace(" руб.", "").strip()
    clean_price = int(raw_price)
    return item_dict["name"], clean_art, clean_price
# Подключение к PostgeSQL
def upload_to_database(products_list):
    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="flashka57rus",
        host="127.0.0.1",
        port="5432"
    )
    cursor = connection.cursor()
# Запускаем цикл по нашему списку
    for row in products_list:
# Отправляем товар в первую функцию на очистку
        name, art, price = clen_item_data(row)
        insert_query = """
            insert into marketplace_products (product_name, clean_article, clean_price)
            values (%s,%s,%s);
        """
        cursor.execute(insert_query,(name, art, price))
        print(f"Товар {name} успешно загружен в базу PostgeSQL!")
    connection.commit()
    cursor.close()
    connection.close()
    print("\n --- Все данные успешно записаны! ---")
upload_to_database(raw_items)