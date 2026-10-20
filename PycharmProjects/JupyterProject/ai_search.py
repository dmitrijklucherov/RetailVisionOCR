# Библиотеки: 1.Асинхронное выполнение кода. 2.Метод векторизации из ML(перевод слов
# в цифры(векторы) и посик совпадений. 3.Метод косинусного сходства из ML(измеряет угол
# между векторами и чем ближе к 1 косинус угла, тем выше схоство)
import asyncio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from data_base import Database

class AISearch:
    # Переводим слова в матрицы(оптимальные значения для русского языка)
    # char_wb - режем слово на куски(n-граммы), ngram_range = (2, 4) - 3 шага нарезки от двух до 4 букв
    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    # Поиск совпадений: 1.Слова от пользователя - str. 2. Список кортежей из БД, полученный через
    # JOIN - list. 3.Количество сопадений - int
    async def find_best_matches(self, user_query: str, db_products: list, limit: int = 3):
        # Защита от пустого сообщения или пустой базы
        if not db_products or not user_query.strip():
            return[]
        # Поиск товара в БД(только текстовые названия)
        product_titles = [prod[2] for prod in db_products]
        # Асинхронный запуск поиска(отдельным фоновым потоком процессора)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._calculate_similarity, user_query, db_products, product_titles, limit)
    # Приватная функция расчета векторов и косинусного сходства
    def _calculate_similarity(self, user_query, db_products, product_titles, limit):
        # Берем все названия из базы, разбиваем их на части(2,3,4) и обучаемся - у каждого слова свой индекс - fit
        # Преобразуем слова в векторы - transform
        tfidf_matrix = self.vectorizer.fit_transform(product_titles)
        # Запрос пользователя тоже в векторы
        query_vector = self.vectorizer.transform([user_query])
        # Ищем процент совпадения с помощью косинуса угла векторов - cosine_similarity
        # Преобразуем матрицу в список - flatten()
        similarity_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
        # Перебираем результаты и  все у кого совпадение больше 30% собираем в список
        scored_products = []
        for index, score in enumerate(similarity_scores):
            if score > 0.30:
                scored_products.append((score, db_products[index]))
        # Сортируем по убыванию
        scored_products.sort(key=lambda x: x[0], reverse=True)
        return [prod_data for score, prod_data in scored_products[:limit]]

    # Тест


# Тест с выводом цен
async def main():
    ai = AISearch()
    db = Database()  # Подключаем наш асинхронный пул базы данных
    await db.connect()

    # Имитируем, что ИИ-поиск отработал и выдал нам список найденных товаров
    # (Добавим в наш mock-тест четвертым элементом актуальную цену товара)
    mock_db_data = [
        (1, 1001, "Картофель фасованный 2кг", 71),  # Цена 71 руб.
        (2, 1002, "Лук репчатый желтый", 44),
        (3, 1003, "Укроп свежий зелень 50г", 64),
        (4, 1004, "Картошка молодая отборная", 198)  # Цена 198 руб.
    ]

    query = "картоха"

    # Запускаем ИИ-поиск (передаем лимит, например, топ-2)
    result = await ai.find_best_matches(query, mock_db_data, limit=2)

    print(f"Запрос: {query}")
    print(f"🤖 ИИ-поиск успешно завершен! Вот что нашлось:")

    # === ТЕПЕРЬ НА ВЫХОДЕ ЕСТЬ ЦЕНА! ===
    for item in result:
        # Извлекаем данные из кортежа: id, артикул, название и цену
        prod_id, sku_id, title, price = item
        print(f"-> Артикул: {sku_id} | {title} — 💰 Цена: {price} ₽")

    await db.disconnect()


if __name__ == "__main__":
    import selectors  # ОБЯЗАТЕЛЬНО: Импортируем системный модуль селекторов

    # 🎯 ОТК-Запуск: Приказываем Windows использовать совместимый движок Selector
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    )




