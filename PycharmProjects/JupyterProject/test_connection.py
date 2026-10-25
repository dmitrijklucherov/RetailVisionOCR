import asyncio
import os
from playwright.async_api import async_playwright
from magnit_parser import get_magnit_data

async def try_connect(page, url: str):
    try:
        # Переходим по ссылке и ждем закгрузку сайта
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Если получили код 200, то определяем что за магазин и передаем на обработку
        if response and response.status ==200:
            # Ждем 2 секунды и забираем html
            await asyncio.sleep(2)
            html_content = await page.content()
            # Определяем какой файл вызвать для разбора по совпадению в ссылке
            if "magnit" in url.lower():
                price, title = await get_magnit_data(html_content)
                if price:
                    print(f"Цена найдена: {price}")
                else:
                    print("Цена не найдена")
            elif response:
                print(f"Ошибка сервера: Статус {response.status}")
            else:
                print("Сервер недоступен")
    except Exception as e:
        print(f"Ошибка: {e}")
async def main():
    url_suite = input("Введите ссылку:") # Для тестов пока так
    if not url_suite:
        return
    # site_name = "Магнит" if "magnit" in url_suite.lower() else "Пятрочка" if "5ka" in url_suite.lower() or "pyaterochka" in url_suite.lower() else "ПАРСЕР"
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
        await try_connect(page, url_suite)
        await asyncio.sleep(10)
        await context.close()

# Тест
if __name__ == "__main__":
    asyncio.run(main())


