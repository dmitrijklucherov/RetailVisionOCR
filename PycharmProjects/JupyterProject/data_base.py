# Скритп №2. Создан 11.09.26 в 21-14
import os
from dotenv import load_dotenv
import psycopg
load_dotenv()

class Database:
    def __init__(self):
        # Забираем пароль из сейфа
        pass_bd = os.getenv("DB_PASSWORD")
        # Устанавливае соединение
        self.connection = psycopg.connect(
            dbname = "postgres", user = "postgres", password = pass_bd, host = "127.0.0.1", port = "5432"
        )
        self.cursor = self.connection.cursor()
    # Реляционная модель для экономии памяти и ускорения обработок
    # Создаем функцию записи и выборки значений в три таблицы для защиты от дублирования
    # Сввязываем таблицы между собой для упрощения взаимодейсвия и каскадной очистки
    def insert_product(self, vk_id, url, sku_id, price_base, price_card, stock_count ):
        query_users = """
            insert into users (vk_id)           
            values (%s)
            on conflict (vk_id) do update set vk_id = excluded.vk_id
            returning user_id;
        """
        self.cursor.execute(query_users, (vk_id,))
        # Возвращаем кортеж из базы - забираем нулевой элемент
        user_id = self.cursor.fetchone()[0]
        query_products = """
            insert into products (user_id, url, sku_id)
            values(%s,%s,%s)
            returning product_id
            """
        self.cursor.execute(query_products, (user_id, url, sku_id))
        product_id = self.cursor.fetchone()[0]
        query_price_history = """
            insert into price_history (product_id, price_base, price_card, stock_count)
            values (%s,%s,%s,%s)
        """
        self.cursor.execute(query_price_history, (product_id, price_base, price_card, stock_count))
    # Функция чтения данных: берем данные из таблиц(p. h.), сокращяя их названия(p, h)
    # Ищем минимальную цену в таблице 'h' строго для товара который нам нужен
    # Ограничиваем поиск по времени, вместо заглушки '%s' будут наши входные данные и результат присваиваем новой переменной 'min_price'
    # Берем таблицу 'p', присоеденяем к ней таблицу 'h' только по совпадению значений 'product_id'
    # Выбираем только те ссылки где есть наше искомое значение '%s', сортируем по дате, возвращаем одно отсортированное значение
    def get_product_analytics_data(self, search_word, months_limit):
        query_products = """
            select p.url, p.sku_id, h.price_base, h.price_card, h.stock_count, 
                (select min(price_card) from price_history where product_id = p.product_id and check_date >= now() - interval '%s month') as min_price
            from products p
            join price_history h on p.product_id = h.product_id
            where p.url like %s
            order by h.check_date desc
            limit 1;
        """
        # Ищем фразу в любой части, % % - отсечение лишнего(все что внутри остается) и сохраняем в новую переменную
        formatted_search = f"%{search_word}%"
        # Передаем значения в базу: 1.Весь запрос. 2.Время в месяцах вместо первой заглушки. 3.Искомое слово вместо второй заглушки
        self.cursor.execute(query_products, (months_limit, formatted_search))
        # Забираем эту строку в виде кортежа и возвращаем
        result = self.cursor.fetchone()
        return result
    # Закрываем соединение
    def disconnect(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        print("Все изменения зафиксированы, соединение закрыто")

# Тест создания и записи кода
if __name__ == "__main__":
    db = Database()
    db.create_table()
    test_item = ("1234", "Тестовая футболка", 993.34, 45, "11-09-2026 23:43")
    db.insert_product(test_item)
    db.disconnect()





