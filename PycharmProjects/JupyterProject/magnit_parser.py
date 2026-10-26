import asyncio
import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup

# 1.Функция поиска цены в HTML
def extract_price_by_html(soup: BeautifulSoup) -> Optional[int]:
    try:
        price_el = soup.find("span", attrs={"data-test-id": "v-product-detail-price-current"})
        if price_el:
            # Методом передора оставляем только цифры и склеваем их
            price_text = "".join([c for c in price_el.text if c.isdigit()])
            if price_text:
                return int(price_text)
    except Exception as e:
        print(f"Ошибка HTL: {e}")
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
    except Exception as e:
        print(f"Ошибка JSON: {e}")
    return None
# Функция сбора данных и предоставления отчета
async def get_magnit_data(html_content: str) -> Tuple[Optional[float ], str]:
    soup = BeautifulSoup(html_content, "html.parser")
    # Извлекаем название товара
    title_el = soup.find("h1")
    title = title_el.text.strip() if title_el else "Товар Магнит"
    print(f"Товар определен: {title}")
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
# Локальные настройки браузера только для "Магнит"
async def process_magnit(page, url: str) -> Tuple[Optional[float], str]:
    try:
        await page.context.add_cookies([{
            "name": "shopCode",
            "value": "%22570061%22",
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
    except Exception as e:
        return None, "Ошибка парсинга"
