import asyncio
import logging
import random
import selectors

from playwright.async_api import async_playwright
from data_base import Database
from test_connection import main

# Настройка записи лога только для этого файла
logging.basicConfig(
    level=logging.INFO,
    filename="logs/cron_update.log",
    filemode="a",
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
db = Database()

# Функция ежедненвного обхода ссылок и обновления цен
async def run_daily_update():
    logging.info("---Запуск автоматичекого обновления цены---")
    # Делаем SQL-запрос и забираем список кортежей(всех уникальных товаров)
    products = db.get_unique_urls_for_update()
    if not products:
        logging.info("База данных товаров пуста.")
        return
    # Перемешиваем товары, что бы они не повторялись ежедневно
    random.shuffle(products)
    # Запускаем браузер с чистой вкладкой
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36")
        page = await context.new_page()
        # Распаковываем кортеж и передаем ссылку в файл определения и распределения ссылок
        # Файл возвращает кортеж с ценой и названием
        for product_code, url in products:
            try:
                price, title = await main(url)
                # Еслм получили цену и название то записываем новую строку в таблицу и логируем результат
                if price is not None:
                    db.insert_cron_price(product_code, price)
                    logging.info(f"[Успех] Товар: {product_code} ({title}) обновлен")
                else:
                    logging.warning(f"[Пропуск, cron] Не удалось взять цену для продукта: {product_code}")
            except asyncio.TimeoutError:
                logging.error(f"[Таймаут, cron] Превышено время ожидания загрузки сайта для товара: {title}")
            except (ValueError, TypeError) as type_error:
                logging.error(f"[Ошибка типов] некоректный формат данных для прродкта: {title}, ошибка: {type_error}")
            except Exception as unexpected_error:
                logging.error(f"[Критический сбой, cron] Непредвиденная ошибка: {unexpected_error}")
            # Генератор случайной задержки выполнения кода
            sleep_time = random.randint(15,55)
            await asyncio.sleep(sleep_time)
        # Завершаем парсинг и очищаем оперативку
        await context.close()
        await browser.close()
    logging.info("---Ежедневное обновление цен успешно завершено!---")

# Тест
if __name__ == "__main__":
    asyncio.run(run_daily_update())

