import psycopg2
def big_marketplace_sales():
    while True:
        limit_price = int(input("Введите лимит цены:"))
        if limit_price < 300:
           print("Слишком маленький лимит! На маркетплейсе нет таких дешёвых товаров. Повторите ввод.")
           continue
        connection = psycopg2.connect(
            dbname = "postgres",
            user = "postgres",
            password = "flashka57rus",
            host = "127.0.0.1",
            port = "5432"
        )
        cursor = connection.cursor()
        select_query = """
            select product_name, price, status
            from big_marketplace_sales
            where price > %s
        """
        cursor.execute(select_query, (limit_price,))
        found_goods = cursor.fetchall()
        cursor.close()
        connection.close()
        total_amount = 0
        total_count = 0
        faled_count = 0
        for row in found_goods:
            name,price,status = row
            if status == "success":
                total_amount += price
                total_count += 1
            else:
                faled_count += 1
        average_count = total_amount/total_count
        average_count = round(average_count,2)
        final_count = {
            "Общая сумма": total_amount,
            "Средний чек": average_count,
            "Количество бракованных заказов": faled_count
        }
        print(final_count)
        return final_count
print(big_marketplace_sales())





