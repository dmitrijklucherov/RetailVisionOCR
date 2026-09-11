import psycopg2
def search_marketplace_bot():
    connection = psycopg2.connect(
        dbname = "postgres",
        user = "postgres",
        password = "flashka57rus",
        host = "127.0.0.1",
        port = "5432"
    )
    cursor = connection.cursor()
    while True:
        max_price = int(input("Какая максимальная цена вас интересует?"))
        if max_price < 15200:
            print(f"Товаров, ниже {max_price} в наличии нет! Повоторите запрос!")
        else:
            select_query = """
                select product_name, article, price
                from big_marketplace_sales
                where price < %s and status = 'success';
            """
            cursor.execute(select_query, (max_price,))
            found_goods = cursor.fetchall()
            cursor.close()
            connection.close()
            print(f"\n ---Найдено товаров дешевле:{max_price} руб.---")
            for row in found_goods:
                name,art,price = row
                print(f"Товар:{name} | Артикул:{art} | Цена:{price} руб.")
            break
search_marketplace_bot()