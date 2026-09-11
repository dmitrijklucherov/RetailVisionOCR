import psycopg2
def find_cheap_products(max_price_limit):
    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="flashka57rus",
        host="127.0.0.1",
        port="5432"
    )
    cursor = connection.cursor()
    select_query = """
        select product_name, clean_article, clean_price
        from marketplace_products
        where clean_price < %s;
    """
    cursor.execute(select_query, (max_price_limit,))
    found_rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return found_rows
search_result = find_cheap_products(int(input("Введите сумму:")))
print("\n ---Ответ бота (строка из базы)---")
for row in search_result:
    name, art, price = row
    print(f"Товар:{name} | Артикул:{art} | Цена:{price}руб.")