import asyncio
import os
from playwright.async_api import async_playwright

async def try_connect(page, url: str, name: str):
    try:
        # Переходим по ссылке и ждем закгрузку сайта
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        status = response.status
        print(f"Status code: {status}")
    except Exception as e:
        print(f"Ошибка: {e}")
async def main():
    url_suite = input("Введите ссылку:") # Для тестов пока так
    if not url_suite:
        return
    site_name = "Магнит" if "magnit" in url_suite.lower() else "Пятрочка" if "5ka" in url_suite.lower() or "pyaterochka" in url_suite.lower() else "ПАРСЕР"
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
        await try_connect(page, url_suite, site_name)
        await asyncio.sleep(10)
        await context.close()

# Тест
if __name__ == "__main__":
    asyncio.run(main())


