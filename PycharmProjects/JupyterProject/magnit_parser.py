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
def extract_price_by_json(html_text: str) -> Optional[int]:
    try:
        match = re.search(r'"actualPrice":\s*(\d+)', html_text)
        if match:
            return int(match.group(1))
        match_fallback = re.search(r'"price":\s*(\d+)', html_text)
        if match_fallback:
            return int(match_fallback.group(1))
    except Exception as e:
        print(f"Ошибка JSON: {e}")
    return None
# Сравниваем весы доверия двух методов и возвращаем отчет
async def get_magnit_data(html_content: str) -> Tuple[Optional[int], str]:
    soup = BeautifulSoup(html_content, "html.parser")
    title_el = soup.find("h1")
    title = title_el.text.strip() if title_el else "Товар Магнит"
    print(f"Товар определен: {title}")
    # Методы сбора данных
    html_price = extract_price_by_html(soup)
    json_price = extract_price_by_json(html_content)
    # Поиск цены: четыре варианта нахождения и возврата цены и названия
    if html_price is not None and json_price is not None:
        html_price = html_price/100
        if html_price == json_price:
            print("Цена верна в обоиx случаях")
            return html_price, title
        else:
           print(f"Оставляем только ту, которой доверяем. Цена1: {html_price}, Цена2: {json_price}")
           return json_price, title
    if html_price is not None:
        print("Остается только цену из json")
        return json_price, title
    if json_price is not None:
        print("Оставляем только цену из html")
        return html_price, title
    return None, title
