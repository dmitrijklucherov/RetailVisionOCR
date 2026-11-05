import asyncio
import logging
import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup

# Ищет подстроку shopCode= или merchantId=, за которой идут цифры (от 5 до 8 знаков)
SHOP_CODE_PATTERN = re.compile(r'(?:shopCode|merchantId)=(?:%22)?(\d{5,8})(?:%22)?')


# 1.Функция поиска цены в HTML
def extract_price_by_html(soup: BeautifulSoup) -> Optional[int]:
    try:
        price_el = soup.find("span", attrs={"data-test-id": "v-product-detail-price-current"})
        if price_el:
            # Методом передора оставляем только цифры и склеваем их
            price_text = "".join([c for c in price_el.text if c.isdigit()])
            if price_text:
                return int(price_text)
    # Проблемы:
    # 1. Изменился HTML
    except AttributeError as attr_error:
        logging.error(f"[Ошибка структуры Магнит: HTML] Изменились HTML-атрибуты цены: {attr_error}")
    # 2. Неверный тип данных
    except ValueError as value_error:
        logging.error(f"[Ошибка типов Магнит: HTML] Не удалось преобразовать текст цены: {value_error}")
    # 3. Все остальные ошибки
    except Exception as unexpected_error:
        logging.error(f"[Критический сбой Магнит: HTML] Непредвиденная ошибка: {unexpected_error}")
    return None

# 2.Функция поиска цены в JSON
def extract_price_by_json(html_text: str) -> Optional[float]:
    try:
        match = re.search(r'"actualPrice":\s*(\d+(?:\.\d+)?)', html_text)
        if match:
            return float(match.group(1))
        # Запасной вариант поиска
        match_fallback = re.search(r'"price":\s*(\d+)', html_text)
        if match_fallback:
            return float(match_fallback.group(1))
    # Проблемы:
    # 1. Неверный тип данных
    except (ValueError, TypeError) as type_error:
        logging.error(f"[Ошибка типов Магнит: JSON] Некорректный формат цены: {type_error}")
    # 2. Все остальные ошибки
    except Exception as unexpected_error:
        print(f"[Критический сбой Магнит: JSON] Непредвиденная ошибка: {unexpected_error}")
    return None

# 3. Функция сбора данных и предоставления отчета
async def get_magnit_data(html_content: str) -> Tuple[Optional[float ], str]:
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Извлекаем название товара
        title_el = soup.find("h1")
        title = title_el.text.strip() if title_el else "Товар Магнит"
        print(f"Товар определен: {title}.")
        # Собираем данные двумя методами
        html_price_raw = extract_price_by_html(soup)
        json_price = extract_price_by_json(html_content)
        # Переводим копейуи в рубли
        html_price = (html_price_raw / 100) if html_price_raw is not None else None
        # Поиск цены: 1.Оба источника. 2.Из HTML. 3.Из JSON скрипта. 4.Ничего не нашли
        if html_price is not None and json_price is not None:
            if html_price == json_price:
                return html_price, title
            else:
                return html_price, title
        if html_price is not None:
            return html_price, title
        if json_price is not None:
            return json_price, title
        return None, title
    # Проблемы:
    # 1. Неверная структура данных
    except AttributeError as attr_error:
        logging.error(f"[Ошибка структуры Магнит: title] Нарушена логика тегов при сборке: {attr_error}")
        return None, "Ошибка разбора структуры Магнит"
    # 2. Все остальные ошибки
    except Exception as unexpected_error:
        logging.error(f"[Критический сбой Магнит: title] Непредвиденная ошибка: {unexpected_error}")
        return None, "Внутренняя ошибка при сборке данных"

# 4. Локальные настройки браузера только для "Магнит"
async def process_magnit(page, url: str) -> Tuple[Optional[float], str]:
    try:
        match = SHOP_CODE_PATTERN.search(url)
        if match:
            extracted_shop = match.group(1)
            current_shop_code = f"%22{extracted_shop}%22"
            print(f"Код магазина: {current_shop_code}")
        else:
            current_shop_code = "%22570061%22"
            print("Код не найден")
        await page.context.add_cookies([{
            "name": "shopCode",
            "value": current_shop_code,
            "domain": "magnit.ru",
            "path": "/"
        }])
        # Переход на страницу с ожиданием 3 сек
        response = await page.goto(url, wait_until="networkidle", timeout=30000)
        # Если нет страницы или код статутса не 200, получаем статус ошибки и возварщаем None
        # Делаем задержку в 2 сек для уверенной работы скрипта и запускаем парсинг
        if not response or response.status != 200:
            status = response.status if response else "Нет ответа"
            return None, "Неизвестный товар"
        await asyncio.sleep(2)
        html_content = await page.content()
        return await get_magnit_data(html_content)
    # Проблемы:
    # 1. Сайт не ответил за указанное в коде время
    except asyncio.TimeoutError:
        logging.error(f"[Таймаут Магнит] Сайт не ответил за 30 сек по ссылке: {url}")
        return None, "превышено время ожидания сайта Магнит"
    # 2. Все остальные ошибки
    except Exception as core_error:
        logging.error(f"[Движок Магнит] Критический сбой сессии: {core_error}")
        return None, "Внутренняя ошибка подсистемы браузера"
