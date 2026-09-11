import psycopg2
def security_function():
    while True:
        limit = int(input("Введие минимальную допустимую цену:"))
        if limit < 500:
            print("У нас нет такой цены! Повторите запрос")
            continue
        else:
            connection = psycopg2.connect(
                dbname = "postgres",
                user = "postgres",
                password = "flashka57rus",
                host = "127.0.0.1",
                port = "5432"
            )
            cursor = connection.cursor()
            sel_query = """
                select product_name, article, price
                from big_marketplace_sales
                where status = 'success' and price < %s
                """
            cursor.execute(sel_query, (limit,))
            found_bad = cursor.fetchall()
            cursor.close()
            connection.close()
            total_anomaly_sum = 0
            anomaly_count = 0
            for bad in found_bad:
                price = bad
                total_anomaly_sum += price
                anomaly_count += 1
            result_anomaly = {
                "Потенциальный убыток": total_anomaly_sum,
                "Количество аномалий": anomaly_count
            }
            print(result_anomaly)
            return result_anomaly
security_function()