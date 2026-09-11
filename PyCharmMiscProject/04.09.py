import psycopg2


class Filter:
    def __init__(self, new_type, new_title, new_price, new_item):
        self.type = new_type.lower()
        self.title = new_title.upper().strip()
        new_price = new_price.replace(" руб.", "").replace(" ", "")
        self.price = int(new_price)
        self.item = new_item

    def return_filter(self):
        return self.type, self.title, self.price, self.item


def connect_baza():
    while True:
        sum_stock = int(
            input("Товар какой стоимости вас интересует: Введите значение, мы подберем товар с ближайшей ценой: "))
        if sum_stock <= 0 or sum_stock >= 100000:
            print(f"Товара с ценой {sum_stock}руб. нет в наличии.")
            continue
        else:
            connection = psycopg2.connect(
                dbname="postgres", user="postgres", password="flashka57rus", host="127.0.0.1", port="5432"
            )
            cursor = connection.cursor()
            insert_stock = """
                select product_type, title, raw_price, item_status
                from messy_marketplace_stock;
            """
            cursor.execute(insert_stock)
            import_stock = cursor.fetchall()
            cursor.close()
            connection.close()

            print(f"\n--- ИЩЕМ ТОВАРЫ В ДИАПАЗОНЕ ОТ {sum_stock * 0.8} ДО {sum_stock * 1.2} РУБ. ---")

            # Переменная-флаг, чтобы узнать, нашли мы хоть что-то во всей базе
            has_results = False

            for row in import_stock:
                type, title, price, item = row
                if item == "failed":
                    continue
                row_stock = Filter(type, title, price, item)
                filter_stock = row_stock.return_filter()
                clean_type, clean_title, clean_price, clean_status = filter_stock

                # СДВИГ ВПРАВО (Внутрь цикла for)! Проверяем КАЖДЫЙ товар на лету!
                int_price = int(clean_price)
                min_price = sum_stock * 0.9
                max_price = sum_stock * 1.1

                if min_price <= int_price <= max_price:
                    print(f"🎯 РЕКОМЕНДУЕМ: {clean_type.upper()} | Модель: {clean_title} | Цена: {int_price} руб.")
                    has_results = True

            # Эта проверка стоит ПОСЛЕ цикла. Если за все 100 строк мы ничего не нашли:
            if not has_results:
                print(f"❌ Извините, товаров в диапазоне цен около {sum_stock} руб. не найдено.")

        break


connect_baza()
