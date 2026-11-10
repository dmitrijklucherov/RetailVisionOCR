import asyncio
import logging
import os
from typing import Tuple, Optional

import requests

from playwright.async_api import async_playwright
from magnit_parser import process_magnit
from ozon_parser import process_ozon, parse_ozon_page_data

# Управляем режимом браузера через .env (для теста на ПК показываем, для сервера нет)
HEADLESS_MODE = os.getenv("HEADLESS", "True").lower() == "true"

# 1. Асинхронная функция приема и распределения ссылки по другим файлам для получения названия и цены
async def try_connect(page, url: str) -> Tuple[Optional[float], str, Optional[int]]:
    try:
        if "magnit" in url.lower():
            price, title = await process_magnit(page, url)
            if price:
                print(f"Товар: {title}. Цена: {price}")
                return price, title, None
            else:
                print("Цена не найдена")
                return None, title, None
        elif "ozon" in url.lower():
            price, title, sku_id = await process_ozon(page, url)
            if price:
                print(f"Товар: {title}. Цена: {price}")
                return price, title, sku_id
            else:
                print("Цена не найдена")
                return None, title, sku_id
        elif "wb" in url.lower():
            return None, "ВБ пока в разработке", None
        else:
            return None, "Неудалось распознать данные нас транице", None
    except requests.exceptions.RequestException as net_error:
        logging.error(f"Ошибка сети при запросе к маркетплейсу: {net_error}")
        return None, "Не удалось соеденится. Проверьте соединение", None
    except (ValueError, KeyError, TypeError) as parse_error:
        logging.error(f"Изменилась структура сайта: {parse_error}")
        return None, "Не удалось распознать данные на странице товара.", None
# 2. Асинхронная функция запуска браузера с помощью cookie из другого файла(пока только магнит)
async def main(url_suite: str):
    if not url_suite:
        return None, "Ошибка! Ссылка пуста"
    async with async_playwright() as p:
        # Временная папка гостевого профиля
        guest_profile = os.path.join(os.getcwd(), "guest_browse_data")
        # Запуск браузера
        context = await p.chromium.launch_persistent_context(
            user_data_dir=guest_profile,
            headless=False,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled", # Маскировка под человека
                "--start-maximized", # Открыть во весь экран
                "--disable-dev-shm-usage", # Запрет использования памяти
                "--no-sandbox", # Безотказный запуск браузера, что бы виндовс не блокировал
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
                "--lang=ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7" # Прикидываемся браузером с языковыми моделями
            ]
        )
        # Берем чистую вкладку
        page=context.pages[0] if context.pages else await context.new_page()
        # Тестируем вход на сайт
        price, title, sku_id = await try_connect(page, url_suite)
        await asyncio.sleep(10)
        await context.close()
        return price, title, sku_id


# Тест
if __name__ == "__main__":
    # Для теста передаем тестовую ссылку прямо в консоли
    test_url = input("Введите ссылку для теста: ")
    if test_url:
        asyncio.run(main(test_url))