# Регулярки для точного поиска данных, модель для полученных результатов, вариации двойных/многочисленных типов, мини-ИИ для интелектуального поиска
import asyncio
import re
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from ai_search import AISearch

# 1.Описываем модель, которую хотим получить: id товара, ссылку, топ товаров, срок анализа, кодовые значения, текст
class FilterMessage(BaseModel):
    product_id: List[int] = Field(default=[], description="Полученный ID товара")
    links: List[str] = Field(default=[], description="Все найденные ссылки")
    top_limit: Optional[int] = Field(default=None, description="Лимит вывода товаров(от 1 до 10)")
    days_depth: Optional[int] = Field(default=0, description="Глубина истории(от 10 до 100)")
    command: Optional[str] = Field(default=None, description="Кодовые знаки")
    clean_text: str = Field(default="", description="Весь чистый текст")
    # Функция распределения ответов
    async def get_report_text(self, db=None, analytics: Optional[Tuple] = None) -> str:
        # 1.Артикул. 2. Ссылка. 3. Непонятное сообщение
        if self.product_id:
            if analytics:
                url, sku_id, current_price, stock, min_price = analytics
                month_limit = self.days_depth if (self.days_depth and self.days_depth > 0) else 1
                return (
                    f"Товар найден через ИИ!\n"
                    f"Артикул: {sku_id}\n"
                    f"Текущая цена: {current_price} руб. (Остаток: {stock} шт.)\n"
                    f"Минимальная цена: {min_price} руб., за {month_limit} мес.\n"
                    f"Ссылка: {url}"
                )
            else:
                return f"Артикул распознан: {self.product_id[0]} Но в базе нет о нем данных"
        if self.links:
            return (
                f"Ссылка получена! Этого товара еще нет в нашей базе данных.\n"
                f"Я передал её в модуль мониторинга цен. Запустил первичный парсинг и анализ, "
                f"совсем скоро история цен появится в системе!"
            )
        return (
            f"Не совсем понял что вы мне прислали. Повторите запрос.\n"
        )

# Класс Фильтр с 4 функциями выборки: id, спецсимволы, управляющие цифры, оставшийся текст
# Для красоты и порядка используем декоратор, что бы функции работали независимо в одном месте
class Filter:
    # Один экземляр поиска для всего класса
    ai_search = AISearch()

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

    # Функция очистки текста. Нужно получить название товара для поиска в базе
    # Убираем ссылки, все цифры и спецзнаки и на всякий случай пробелы.
    @staticmethod
    async def filter_clean_text(text: str, found_links: List[str]) -> str:
        text_clear = text
        for link in found_links:
            text_clear = text_clear.replace(link, "")
        text_clear = re.sub(r'\d+', '', text_clear)
        clean_words = re.sub(r'[^a-zA-Zа-яА-ЯёЁ\s]', '', text_clear).strip()
        text_clear_spaces = re.sub(r'\s+', ' ', clean_words)
        final_clean_text = text_clear_spaces.strip()
        return final_clean_text

    # Принимаем сообщения распределяем их по методам и собираем модель
    @classmethod
    async def clean_message(cls, raw_text: str, db_connection=None) -> FilterMessage:
        raw_text_stripped = raw_text.strip()
        command = await cls.filter_command(raw_text_stripped)
        if command:
            return FilterMessage(command=command)

        # 1. Вытаскиваем все ссылки из сообщения
        found_links = re.findall(r'https?://\S+', raw_text_stripped)

        # 2. Ищем артикулы в тексте ссылки (убираем \b, чтобы ловить внутри путей /catalog/12345/)
        id_pattern = re.compile(r'\d{7,11}')
        found_ids = [int(n) for n in id_pattern.findall(raw_text_stripped) if int(n) != 0]

        # 3. Полностью очищаем текст от ссылок
        text_for_analytics = raw_text_stripped
        for link in found_links:
            text_for_analytics = text_for_analytics.replace(link, "")

        # Собираем лимиты и чистим слова
        # Вычисляем числа для статистики и вытаскиваем текст
        top_limit, days_depth = await cls.filter_analytics_trigger(text_for_analytics, found_ids)
        clean_text_words = await cls.filter_clean_text(raw_text_stripped, found_links)

        # 🎯 ЗАЩИТА: Если в сообщении изначально БЫЛА ссылка (found_links),
        # мы ЖЕСТКО запрещаем текстовый ИИ-поиск, даже если в тексте остались хвосты параметров (?size=...)
        if not found_ids and not found_links and len(clean_text_words) > 2 and db_connection is not None:
            all_products = await db_connection.get_all_products_for_ai()
            if all_products:
                best_matches = await cls.ai_search.find_best_matches(clean_text_words, all_products, limit=3)
                for match in best_matches:
                    if isinstance(match, (tuple, list)) and len(match) > 1:
                        sku_id = match[1]
                        if int(sku_id) != 0:
                            found_ids.append(int(sku_id))

        # Собираем готовую модель.
        # Если артикул из ссылки вытащен — он будет в product_id.
        # Если ссылка есть, но артикула в ней нет (не парсится регуляркой) — сработает сценарий новой ссылки.
        # print(FilterMessage(
        #     product_id=found_ids,
        #     links=found_links,
        #     command=command,
        #     top_limit=top_limit,
        #     days_depth=days_depth,
        #     clean_text=clean_text_words
        # )
        return FilterMessage(
            product_id=found_ids,
            links=found_links,
            command=command,
            top_limit=top_limit,
            days_depth=days_depth,
            clean_text=clean_text_words
        )





















