import os
import json
import re
import asyncio
import logging

from typing import Optional, Tuple
from bs4 import BeautifulSoup

# 1. Ищем цену внутри JSON по Ozon карте
def get_price_from_json(soup: BeautifulSoup) -> Optional[float]:
    raw_price = ""
    try:
        # Ищем div, id которого содержит маркер "state-webPrice"
        price_div = soup.find("div", id=lambda x: x and "state-webPrice" in x)
        # Если блока нет(например товара нет в наличии)
        if not price_div:
            logging.warning("[парсер Озон] Блок: 'state-webPrice' отсутствует")
            return None
        # Если блок есть, вытаскиваем регуляркой "cardPrice", очищаем и переводим в число
        if price_div and price_div.has_attr("data-state"):
            state_data = str(price_div["data-state"])
            price_match = re.search(r'"cardPrice"\s*:\s*"([^"]+)"', state_data)
            if price_match:
                raw_price = price_match.group(1)
                cleaned_price = (
                    raw_price.replace("₽", "")
                    .replace("\xa0","")
                    .replace("\u2009", "")
                    .replace(" ", "")
                    .strip()
                )
                return float(cleaned_price)
            else:
                logging.warning("[Парсер Озон] Ключ 'cardPrice' не найден")
                return None
    # Проблемы:
    # 1 Если объекта не существует
    except AttributeError as attr_error:
        logging.error(f"[Ошибка структуры Озон: JSON] Нарушена логика тегов div/data-state: {attr_error}")
    # 2. Если после очистки остались символы или буквы и float() не сработал
    except ValueError as float_error:
        logging.error(f"[Ошибка типов Озон: JSON] Не удалось преобразовать строку: {raw_price} в число: {float_error}")
    # 3. Все остальные ошибки
    except Exception as unexpected_error:
        logging.error(f"[Критический сбой Озон: JSON] Непредвиденная ошибка: {unexpected_error}")
    return None
# 2. Ищем цену в HTML
def get_price_from_html(soup: BeautifulSoup) -> Optional[float]:
    # Создаем переменную заранее для доступа во всех блоках
    raw_price = ""
    try:
        # Ищем тег span, в котором содержится цена
        price_tag = soup.find("span", class_=lambda x: x and "tsHeadline600Large" in x)
        # Если тега нет, записываем в лог и возвращаем None
        if not price_tag:
            logging.warning("[Парсер Озон] Класс: 'tsHeadline600Large' не найден")
            return None
        # Если тег присутствует забираем из него текст, очищаем и переводим в число
        if price_tag:
            raw_price = price_tag.get_text(strip=True)
            cleaned_price = (
                raw_price.replace("₽", "")
                .replace("\xa0", "")
                .replace("\u2009", "")
                .replace(" ", "")
                .strip()
            )
            return float(cleaned_price)
    # Проблемы:
    # 1. Если структура дерева нарушена
    except AttributeError as attr_error:
        logging.error(f"Ошибка структуры Озон: HTML] Нарушена логика тегов: {attr_error}")
    # 2. Если плохо очищен текст
    except (ValueError, TypeError) as float_error:
        logging.error(f"[Ошибка типов Озон: HTML] Не удалось преобразовать текст {raw_price} в число: {float_error}")
    # 3. Все остальные ошибки
    except Exception as unexpected_error:
        logging.error(f"[Критический сбой Озон: HTML] Непредвиденная ошибка: {unexpected_error}")
    return None
# 3. Собираем цены JSON и HTML, сравниваем их и возвращаем результат
def parse_ozon_page_data(html_content: str, url: str) -> Tuple[Optional[float], str]:
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Извлекаем название товара
        title_tag = soup.find("h1", class_=lambda x: x and "tsHeadline" in x) or soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Товар Озон"
        # Вызываем функции для поиска цен
        json_card_price = get_price_from_json(soup)
        html_page_price = get_price_from_html(soup)
        # Проверка поиска в консоли
        print("---Проверка цен  Озон---")
        print(f"Название товара: {title}")
        print(f"Цена с картой JSON: {json_card_price}")
        print(f"Цена из HTML-страницы: {html_page_price}")
        # Выбираем цену, которая пойдет дальше, с подстраховкой
        # Если не смогли достать из JSON, то берем из HTML
        final_price = json_card_price if json_card_price is not None else html_page_price
        return final_price, title
    # Проблемы:
    # 1. Неверная структура чтения данных
    except AttributeError as attr_error:
        logging.error(f"[Ошибка структуры Озон: title] Сбой извлечения текстовых тегов: {attr_error}")
        return None, "Ошибка разбора структуры названия"
    # 2. Неверные типы данных
    except (ValueError, TypeError) as type_error:
        logging.error(f"[Ошибка типов Озон: title] Некорректный формат данных: {type_error}")
        return None, "Ошибка обработки типов данных"
    except Exception as unexpected_error:
        logging.error(f"[Критический сбой Озон: title] Непредвиденная ошибка: {unexpected_error}")
        return None, "Внутренняя ошибка парсера"
# Асинхронная функция управления браузером, принимает объкст страници и ссылку
# Возваращает кортеж из двух элементов
# Локальные настройки только для OZON
async def process_ozon(page, url: str) -> Tuple[Optional[float], str]:
    # Запускаем Озон с полным набором сессионных кук
    try:
        cookies_file = "ozon_cookies.json"
        # Если файл существует то открываем в режиме чтения с указанием кодировки
        if os.path.exists(cookies_file):
            with open(cookies_file, "r", encoding="utf-8") as f:
                # Преобразуем JSON файла в список словарей и подставляем в текущую сессию
                ozon_cookies = json.load(f)
                await page.context.add_cookies(ozon_cookies)
                print(f"Успешно: {len(ozon_cookies)}шт.")
        # Если файла нет, то предупреждаем об этом и продолжаем
        else:
            print(f"Предупреждение! Файл: {cookies_file} не найден!")
        # Маскируемся под переход из поисковой системы
        await page.set_extra_http_headers({
            "Referer": "https://google.com",
            "Accept-Language": "ru-RU,ru;q=0.9"
        })
        # Выполняем переход c задержкой 3 сек
        response = await page.goto(url, wait_until="networkidle", timeout=30000)
        # Если нет страницы или код статутса не 200, получаем статус ошибки и возварщаем None
        # Делаем задержку в 2 сек для уверенной работы скрипта и запускаем парсинг
        if not response or response.status != 200:
            status = response.status if response else "Нет ответа"
            print(f"Ошибкка сети Озон: {status}")
            return None, f"Ошибка доступа: {status}"
        await asyncio.sleep(2)
        html_content = await page.content()
        return parse_ozon_page_data(html_content, url)
    # Проблемы:
    # 1. Превышение лимита загрузки более 30 сек
    except asyncio.TimeoutError:
        return None, "Ошибка: Превышено время ожидания OZON"
    # 2. Проблемы с файлом кук: повреждение или отсутствие
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None, f"Ошибка авторизации: Поврежден файл кук, {e}"
    # 3. Все остальные случаи
    except Exception as e:
        return None, f"Критический сбой Озон: ({type(e).__name__})"







