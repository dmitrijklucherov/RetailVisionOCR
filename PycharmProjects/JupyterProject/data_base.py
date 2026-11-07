import os

from dotenv import load_dotenv
from psycopg import AsyncConnection

load_dotenv()

class Database:
    def __init__(self):
        # Забираем пароль из сейфа
        self.pass_bd = os.getenv("DB_PASSWORD")
    # Функция с параметрами для коннекта с PostgreSQL
    def _get_db_config(self) -> dict:
            return {
                "dbname": "postgres",
                "user": "postgres",
                "password": self.pass_bd,
                "host": "127.0.0.1",
                "port": "5432"
            }
    # Асинхронная функция для записи данных сразу в три таблицы и возврата всей истории цены
    async def insert_and_retail_data(self, vk_id, url, sku_id, price, stock_count, title):
        # Блокируем запись нулей в цену и id
        if sku_id == 0 or price == 0:
            return None

        # Автоматическое формирование уникального индефекатора товара в зависимости от маркетплейса
        url_lower = url.lower()
        if "cosmetic.magnit" in url_lower:
            marketplace = "MK" # Для Магнита-Косметика
        elif "magnit" in url_lower:
            marketplace = "M" # Для Магнита
        elif "ozon" in url_lower:
            marketplace = "O" # Для Озон
        else:
            marketplace = "U" # Не определено
        product_code = f"{marketplace}_{sku_id}"

        # Асинхронное соединение
        async with await AsyncConnection.connect(**self._get_db_config()) as conn:
            async with conn.cursor() as cursor:

                # Запись или обновление уникального товара
                query_products = """
                    insert into products (product_code, marketplace, sku_id, url, title)
                    values (%s, %s, %s, %s, %s)
                    on conflict (product_code) do update set
                        url = excluded.url,
                        title = excluded.title
                    returning product_code;
                """
                await cursor.execute(query_products, (product_code, marketplace, sku_id, url, title))
                # Забираем id
                p_code_row = await cursor.fetchone()
                if not p_code_row:
                    return None
                db_product_code = p_code_row[0]

                # Привязываем пользователя к уникальному товару
                query_subscriptions = """
                    insert into user_subscriptions (vk_id, product_code)
                    values (%s, %s)
                    on conflict (vk_id, product_code) do nothing;
                """
                await cursor.execute(query_subscriptions, (vk_id, db_product_code))

                # Запись новой строки в историю цен
                query_price_history = """
                    insert into price_history (product_code, price, check_date)
                    values (%s, %s, now());
                """
                await cursor.execute(query_price_history, (db_product_code, price))

                # Выборка всей накопленной истории цен для анализа
                query_select_history = """
                    select price, to_char(check_date, 'YYYY-MM-DD HH24:MI:SS')
                    from price_history
                    where product_code = %s
                    order by check_date desc;
                """
                await cursor.execute(query_select_history, (db_product_code,))
                # Забираем все строки из базы
                return await cursor.fetchall()

    # Функция чтения данных: берем данные из таблиц(p. h.), сокращяя их названия(p, h)
    # Ищем минимальную цену в таблице 'h' строго для товара который нам нужен
    # Ограничиваем поиск по времени, вместо заглушки '%s' будут наши входные данные и результат присваиваем новой переменной 'min_price'
    # Берем таблицу 'p', присоеденяем к ней таблицу 'h' только по совпадению значений 'product_id'
    # Выбираем только те ссылки где есть наше искомое значение '%s', сортируем по дате, возвращаем одно отсортированное значение
    async def get_product_analytics_data(self, search_word, months_limit):
        query_products = """
            select p.url, p.product_code, h.price, 
                (select min(price) from price_history where product_code = p.product_code and check_date >= now() - make_interval (months => %s)) as min_price
            from products p
            join price_history h on p.product_code = h.product_code
            where p.title like %s
            order by h.check_date desc
            limit 1;
        """
        # Ищем фразу в любой части, % % - отсечение лишнего(все что внутри остается) и сохраняем в новую переменную
        formatted_search = f"%{search_word}%"
        async with await AsyncConnection.connect(**self._get_db_config()) as conn:
            async with conn.cursor() as cursor:
                # Передаем значения в базу: 1.Весь запрос. 2.Время в месяцах вместо первой заглушки. 3.Искомое слово вместо второй заглушки
                await cursor.execute(query_products, (months_limit, formatted_search))
                # Забираем эту строку в виде кортежа и возвращаем
                return await cursor.fetchone()

    # Функция для ежедневного обновления по расписанию
    async def get_unique_urls_for_update(self):
        # Возвращаем список всех уникальных ссылок для ежедневного парсинига
        query = "select products_code, url from products;"
        async with await AsyncConnection.connect(**self._get_db_config()) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                return await cursor.fetchall()
    # Функция выгрузки данных из базы в нейросеть
    async def get_all_products_for_ai(self):
        async with await AsyncConnection.connect(**self._get_db_config()) as conn:
            async with conn.cursor() as cursor:
                query_ai = """
                    select product_id, sku_id, title, url
                    from products;
                """
                await cursor.execute(query_ai)
                return await cursor.fetchall()







