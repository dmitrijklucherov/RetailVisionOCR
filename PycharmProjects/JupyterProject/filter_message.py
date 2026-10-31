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
    links: List[str] = Field(default=[], description="Все найденные ссылки")
    top_limit: Optional[int] = Field(default=None, ge=1, le=5, description="Лимит вывода товаров(от 1 до 5)")
    days_depth: Optional[int] = Field(default=None, ge=6, le=99, description="Глубина истории(от 6 до 100)")
    command: Optional[str] = Field(default=None, description="Кодовые знаки")
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

# 2. Функция определения и распределения полученной ссылки
def filter_url(raw_text: str) -> Optional[str]:
    found_links = URL_PATTERN.findall(raw_text)
    if not found_links:
        return None

    if len(found_links) > 1:
        return "Ошибка! Я могу обработать только одну ссылку!"

    target_url = found_links[0]
    logging.info(f"В сообщении обнаружена ссылка: {target_url}")
    price_report = asyncio.run(main(target_url))
    return price_report

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
# =====================================================================
def analyze_message(raw_text: str, peer_id: int) -> str:
    # Проверка на наличие ссылок
    url_reply = filter_url(raw_text)
    if url_reply:
        return url_reply

    # Проверка на секретные команды
    command_reply = filter_command(raw_text)
    if command_reply:
        return command_reply

    # Шаг 3: Текстовый поисковый запрос
    # Создаем пустую модель и наполняем её через парсер чисел
    model_data = FilterMessage()
    parsed_model = parse_text_and_numbers(raw_text, model_data)
    if not parsed_model.clean_text:
        return "Запрос пуст. Пожалуйста, напишите название товара."

   # Требует доработки!!!  TODO: WARNING: Отправляем готовую заполненную модель на анализ данных
    try:
        search_result = "Тут заглушка" # process_text_recognition(parsed_model, peer_id)
        return search_result
    # Перехватываем ошибки разбора или анализа данных и отправляем ошибку дальше, Боту.
    except (ValueError, KeyError, TypeError) as search_error:
        logging.error(f"Ошибка обработки: {search_error}")
        raise search_error
