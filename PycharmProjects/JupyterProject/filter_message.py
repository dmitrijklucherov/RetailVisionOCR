import asyncio
import logging
import os
import re

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from test_connection import main

# 1. Формируем модель данных
class FilterMessage(BaseModel):
    product_id: List[int] = Field(default=[], description="Полученный ID товара")
    link: List[str] = Field(default=[], description="Все найденные ссылки")
    top_limit: Optional[int] = Field(default=None, ge=1, le=5, description="Лимит вывода товаров(от 1 до 5)")
    days_depth: Optional[int] = Field(default=None, ge=6, le=99, description="Глубина истории(от 6 до 100)")
    price: Optional[float] = Field(default=None, description="Актуальная цена")
    title: Optional[str] = Field(default=None, description="Название товара")
    clean_text: str = Field(default="", description="Весь чистый текст")

    # Защита от записи нуля в top_limit и days_depth
    @field_validator('top_limit', 'days_depth')
    @classmethod
    def prevent_zero(cls, value: Optional[int]) -> Optional[int]:
        if value == 0:
            return None
        return value


# Регулярные выражения создаются один раз при запуске модуля для ускорения процесса
URL_PATTERN = re.compile(r'\bhttps?://[^\s,]+')
NUMBER_PATTERN = re.compile(r'\b\d{1,2}\b')
SKU_ID = re.compile(r'\b\d{7,11}\b')

# 2. Функция определения и распределения полученной ссылки
def filter_url(raw_text: str, current_model: FilterMessage) -> Optional[FilterMessage]:
    found_links = URL_PATTERN.findall(raw_text)
    found_id = SKU_ID.findall(raw_text)
    if not found_links:
        return None

    if len(found_links) > 1:
        current_model.clean_text = "Ошибка! Я могу обработать только одну ссылку!"
        return current_model

    target_url = found_links[0]
    logging.info(f"В сообщении обнаружена ссылка: {target_url}, ID: {found_id}")
    price_report, title = asyncio.run(main(target_url))
    current_model.link = [target_url]
    current_model.product_id = [int(i) for i in found_id]
    current_model.price = price_report
    current_model.title = title
    if price_report:
        current_model.clean_text = f"Товар: {title} с ценой: {price_report} успешно добавлен в Базу"
    else:
        current_model.clean_text = f"Товар: {title} найден, но на странице нет актуальной цены"
    print(current_model)
    return current_model

# 3. Функция приема спецкоманд
def filter_command(raw_text: str) -> Optional[str]:
    try:
        cleaned_text = raw_text.strip()
        raw_commands = os.getenv("SPECIAL_COMMANDS", "")
        special_commands = [cmd.strip() for cmd in raw_commands.split(",") if cmd.strip()]
        # Сгенерированные в список команды перебираем и сравниваем с данными из .env
        for cmd in special_commands:
            if cleaned_text.startswith(cmd):
                logging.info(f"Сработал секретный ключ: {cmd}")
                if cmd == "###": # Потом изменить
                    logging.warning("Вызван удаленный перезапуск системы")
                    return "Перезагружаю систему"
                elif cmd == "@@@":
                    logging.info("Запрошен список пользователей бота")
                    return "Список пользователей"
    # Перехватываем системные ошибки, такие как сбой доступа к окружению
    except OSError as sys_error:
        logging.error(f"Критическая ошибка операционной системы: {sys_error}")
        return "Внутренняя системная ошибка при обработке команды"
    # Перехватываем ошибки неверных типов данных, если .env поврежден
    except (ValueError, KeyError, TypeError) as config_error:
        logging.error(f"Ошибка конфигурации ли типов данных: {config_error}")
        return "Ошибка конфигурации"
    return None
# 4. Функция поиска чисел(лимитов и дней) и текста для анализа запроса
def parse_text_and_numbers(raw_text: str, current_model: FilterMessage) -> FilterMessage:
    try:
        # Собираем все числа из текста
        numbers = {int(num) for num in NUMBER_PATTERN.findall(raw_text)}

        # Ищеми максимальный top_limit (от 1 до 5)
        valid_top_limits = [n for n in numbers if 1 <= n <= 5]
        if valid_top_limits:
            max_top = max(valid_top_limits)
            current_model.top_limit = max_top

        # Ищем максимальный days_depth (от 6 до 99)
        valid_days_depth = [n for n in numbers if 6 <= n <= 99]
        if valid_days_depth:
            max_days = max(valid_days_depth)
            current_model.days_depth = max_days

        # Сохраняем текст как есть для дальнейшего анализа
        current_model.clean_text = raw_text.strip()
    # Перехват неверных типов данных
    except (ValueError, TypeError) as data_error:
        logging.error(f"Ошибка обработки типов данных: {data_error}")
        current_model.clean_text = raw_text.strip()
    return current_model

# 5. Функция распределения принимаемых данных
def analyze_message(raw_text: str, peer_id: int) -> str:
    # 1. Проверка на спецкомандs (выполняется сразу, без модели)
    command_reply = filter_command(raw_text)
    if command_reply:
        return command_reply

    # Создаем модель в самом начале
    model_data = FilterMessage()

    # 2. Проверяем наличие ссылок, отправляем на анализ и вполучаем модель
    if URL_PATTERN.search(raw_text):
        filled_url_model = filter_url(raw_text, model_data)
        return filled_url_model.clean_text

    # 3 Проверка на текстовый запрос (если ссылки в сообщении не было)
    parsed_model = parse_text_and_numbers(raw_text, model_data)
    if not parsed_model.clean_text:
        return "Запрос пуст. Пожалуйста, напишите название товара."

    print(f"Текстовая модель успешно собрана: {parsed_model}")

    # 4 Временная заглушка для ИИ-поиска
    try:
        # Пока ИИ-поиск process_text_recognition временно отключен,
        search_result = f"Ищем: '{parsed_model.clean_text}' | Топ: {parsed_model.top_limit} | Дней: {parsed_model.days_depth}"
        return search_result

    except (ValueError, KeyError, TypeError) as search_error:
        logging.error(f"Ошибка ИИ-обработки текстового запроса: {search_error}")
        raise search_error





