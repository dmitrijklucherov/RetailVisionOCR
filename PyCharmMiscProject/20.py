import psycopg2
def control_price():
    while True:
        amount = int(input("Введите минимальную стоимсоть брака:"))
        if amount > 20000:
            print(f"У нас нет товаров дороже {amount}. Повторите ввод")
            continue
        else:
            connection = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="flashka57rus",
                host="127.0.0.1",
                port="5432"
            )
            cursor = connection.cursor()
            select_query = """
                select product_name, article, price
                from big_marketplace_sales
                where status = 'failed' and price > %s
            """
            cursor.execute(select_query, (amount,))
            found_goods = cursor.fetchall()
            cursor.close()
            connection.close()
            total_loss = 0
            loss_count = 0
            for row in found_goods:
                name,article,price = row
                total_loss += price
                loss_count += 1
            total_count = {
                "Сумма потерь": total_loss,
                "Количество позиций": loss_count
            }
            print(total_count)
            return total_count
control_price()