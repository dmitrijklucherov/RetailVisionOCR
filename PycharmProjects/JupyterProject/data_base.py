import asyncio
import os
import selectors
from dotenv import load_dotenv
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
load_dotenv()

class Database:
    def __init__(self):
        # Забираем пароль из сейфа
        self.pool = None
        self.pass_bd = os.getenv("DB_PASSWORD")

    async def connect(self):
        # Передаем параметры базы напрямую в пул именованными аргументами
        # kwargs указывает пулу, какие параметры использовать для каждого нового коннекта
        self.pool = AsyncConnectionPool(
            kwargs={
                "dbname": "postgres",
                "user": "postgres",
                "password": self.pass_bd,
                "host": "127.0.0.1",
                "port": "5432"
            },
            min_size=4,  # Стартовое количество соединений
            max_size=20,  # Максимальное количество соединений
            open=False  # Не открываем пул мгновенно в конструкторе
        )
        # Явно запускаем пул и ждем, пока он создаст минимальные подключения
        await self.pool.open()
        print("Асинхронный пул соединений успешно запущен и готов к работе!")
    # Асинхронная функция для записи данных сразу в три таблицы и возврата всей истории цены
    async def insert_and_retail_data(self, vk_id, url, sku_id, price, stock_count, title):
        # Блокируем запись нулей в цену и id
        if sku_id == 0 or price == 0:
            return None
        # Асинхронное бесзопасное соединение
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                # Запись или обновление id с защитой от повторов - on conflict
                query_users = """
                    insert into users (vk_id) 
                    values (%s)
                    on conflict (vk_id) do update set vk_id = excluded.vk_id
                    returning user_id;
                """
                await cursor.execute(query_users, (vk_id,))
                # Забираем id
                user_id = (await cursor.fetchone())[0]
                # Запись или обновление продукта с защитой от повторов
                query_products = """
                    insert into products (user_id, url, sku_id, title)
                    values (%s, %s, %s, %s)
                    on conflict (sku_id) do update set 
                        url = excluded.url,
                        title = excluded.title
                    returning product_id;
                """
                await cursor.execute(query_products, (user_id, url, sku_id, title))
                # Забираем id продукта
                product_id = (await cursor.fetchone())[0]
                # Запись новой строки в историю цен
                query_price_history = """
                    insert into price_history (product_id, price, stock_count, check_date)
                    values (%s, %s, %s, now());
                """
                await cursor.execute(query_price_history, (product_id, price, stock_count))
                # Выборка всей накопленной истории цен для анализа
                query_select_history = """
                    select price, stock_count, to_char(check_date, 'YYYY-MM-DD HH24:MI:SS')
                    from price_history
                    where product_id = %s
                    order by check_date desc;
                """
                await cursor.execute(query_select_history, (product_id,))
                # Забираем все строки из базы
                return await cursor.fetchall()
    # Функция чтения данных: берем данные из таблиц(p. h.), сокращяя их названия(p, h)
    # Ищем минимальную цену в таблице 'h' строго для товара который нам нужен
    # Ограничиваем поиск по времени, вместо заглушки '%s' будут наши входные данные и результат присваиваем новой переменной 'min_price'
    # Берем таблицу 'p', присоеденяем к ней таблицу 'h' только по совпадению значений 'product_id'
    # Выбираем только те ссылки где есть наше искомое значение '%s', сортируем по дате, возвращаем одно отсортированное значение
    async def get_product_analytics_data(self, search_word, months_limit):
        query_products = """
            select p.url, p.sku_id, h.price, h.stock_count, 
                (select min(price) from price_history where product_id = p.product_id and check_date >= now() - make_interval (month => %s)) as min_price
            from products p
            join price_history h on p.product_id = h.product_id
            where p.url like %s
            order by h.check_date desc
            limit 1;
        """
        # Ищем фразу в любой части, % % - отсечение лишнего(все что внутри остается) и сохраняем в новую переменную
        formatted_search = f"%{search_word}%"
        async with self.pool.cursor() as conn:
            async with conn.cursor() as cursor:
                # Передаем значения в базу: 1.Весь запрос. 2.Время в месяцах вместо первой заглушки. 3.Искомое слово вместо второй заглушки
                await cursor.execute(query_products, (months_limit, formatted_search))
                # Забираем эту строку в виде кортежа и возвращаем
                return await cursor.fetchone()
    # Закрываем соединение
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("Все изменения зафиксированы, соединение закрыто")

# Тест создания и записи кода
async def main():
    db = Database()
    try:
        await db.connect()
        print("База успешно подключена!")

        # Тестируем наш асинхронный комбайн обновленным запросом розницы!
        analysis_result = await db.insert_and_retail_data(
            "99", "https://magnit.ru", 900000008, 150, 10, "Картофель фасованный Магнит"
        )
        print(f"Результат: {analysis_result}")

    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА ПОДКЛЮЧЕНИЯ: {repr(e)}\n")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    # Принудительно приказываем Windows запустить совместимый асинхронный движок
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    )






