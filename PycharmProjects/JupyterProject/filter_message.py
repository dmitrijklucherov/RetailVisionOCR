# Регулярки для точного поиска данных, модель для полученных результатов, вариации двойных/многочисленных типов
import re
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple


# 1.Описываем модель, которую хотим получить: id товара, ссылку, топ товаров, срок анализа, кодовые значения, текст
class FilterMessage(BaseModel):
    product_id: List[int] = Field(default=[], description="Полученный ID товара")
    links: List[str] = Field(default=[], description="Все найденные ссылки")
    top_limit: Optional[int] = Field(default=None, description="Лимит вывода товаров(от 1 до 10)")
    days_depth: Optional[int] = Field(default=0, description="Глубина истории(от 10 до 100)")
    commands: Optional[str] = Field(default=None, description="Кодовые знаки")
    clean_text: str = Field(default="", description="Весь чистый текст")
# Класс Фильтр с 4 функциями выборки: id, спецсимволы, управляющие цифры, оставшийся текст
# Для красоты и порядка используем декоратор, что бы функции работали независимо в одном месте
class Filter:
    @staticmethod
    async def filter_url(text: str) -> List[int]:
        # Перебираем весь текст и ищем https:// Причем s - необязательно. Конец ссылки это пробел
        found_links = re.findall(r'https?://\S+', text)
        # Если ссылок нет, возвращаем пустой список
        if not found_links:
            return []
        # Обьеденяем все ссылки  в одну строку, что бы искать id только в них
        links_str = " ".join(found_links)
        # Находим id, зная что там от 7 до 11 символов, переводим его в число и складываем в список
        id_pattern = re.compile(r'\b\d{7,11}\b')
        found_ids = [int(n) for n in id_pattern.findall(links_str)]
        return found_ids
    # Находим спецсимволы, при условии что в сообщении может быть только один код и все
    # Убираем пробелы, переводим в нижний регистр, создаем словарь ключей-значений и ищем совпадения
    @staticmethod
    async def filter_command(raw_command: str) -> Optional[str]:
        clean_raw_text = raw_command.strip().lower()
        special_commands_map = {
            "!$:": "show_most_profitable",
            "!^!": "vk_bot_restart"
        }
        # Переменная которая проверяет совпадение со спецсимволом, будет пустая пока не совпадет
        command = None
        if clean_raw_text in special_commands_map:
            command = special_commands_map[clean_raw_text]
        return command
    # Находим в тексте короткие(до 3-х знкаов) числа для сбора информации, анализа, статистики
    # Пропускам ссылки полностью, задаем кол-во цифр - не более 3 и
    @staticmethod
    async def filter_analytics_trigger(text: str, found_ids: List[int]) -> Tuple[Optional[int], Optional[int]]:
        # Собираем все цифры из сообщения и фильтруем их
        all_numbers = [int(n) for n in re.findall(r'\d+', text)]
        # Отбрасываем все что не попадает в значения от 0 до 99 включительно
        control_list = [num for num in all_numbers if 0 < num <= 99 and num not in found_ids]
        # Отсекаем пустоту
        if not control_list:
            return None, None
        # Сортируем по возрастанию, создаем пустые ячейки для защиты от ошибок если цифр вообще не будет в сообщении
        control_list.sort()
        top_limit, days_depth = None, None
        # Проверям совпадение цифр и если они подходят возварщаем их значения, если нет то ничего
        if control_list:
            min_num = control_list[0]
            if 0 < min_num <= 10:
                top_limit, days_depth = min_num, None
                if len(control_list) > 1:
                    top_limit, days_depth = min_num, control_list[-1]
            else:
                top_limit, days_depth = None, control_list[-1]
        return top_limit, days_depth

















