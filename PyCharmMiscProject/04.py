import psycopg2


# ЦЕХ №1: КЛАСС (Робот-очиститель и калькулятор скидок)
class ElectronicsConverter:
    def __init__(self, title, raw_price):
        self.title = title.strip()  # На лету срезаем пробелы у имени

        # Зачищаем цену от пробелов и букв "руб."
        clean_money = raw_price.replace("руб.", "").strip()
        self.price = int(clean_money)

    # Кнопка №2: Рассчитывает цену со скидкой 10%
    def get_discount_price(self):
        discount_price = self.price * 0.9
        return int(round(discount_price))  # Возвращаем целое округленное число


# ЦЕХ №2: ГЛАВНЫЙ УПРАВЛЕНЕЦ
def process_electronics():
    # ШАГ 1: ПОДКЛЮЧАЕМСЯ К СУБД И ВЫГРЕБАЕМ ДАННЫЕ
    connection = psycopg2.connect(
        dbname="postgres", user="postgres", password="flashka57rus", host="127.0.0.1", port="5432"
    )
    cursor = connection.cursor()

    # Забираем со склада все 4 нужные колонки
    query_clean = """
        SELECT product_type, title, raw_price, item_status
        FROM messy_marketplace_stock;
    """
    cursor.execute(query_clean)
    found_clean = cursor.fetchall()  # Забрали все 100 строк в память Python

    # ШАГ 2: СРАЗУ ЗАКРЫВАЕМ ВЕНТИЛИ БАЗЫ (Она нам больше не нужна)
    cursor.close()
    connection.close()

    print(f"--- ДАННЫЕ ВЫГРУЖЕНЫ (ВСЕГО {len(found_clean)} СТРОК). НАЧИНАЕМ АНАЛИТИКУ ---\n")

    total_sum = 0  # Счётчик для финальной суммы упущенной выгоды

    # ШАГ 3: ЗАПУСКАЕМ ТРАНСПОРТЁРНУЮ ЛЕНТУ ПО ВЫКАЧАННЫМ СТРОКАМ
    for row in found_clean:
        # Распаковываем круглые скобки кортежа на 4 понятные детали
        p_type, title, raw_price, status = row

        # ШАГ 4: ЖЁСТКИЙ ФИЛЬТР БРАКА НА ВХОДЕ
        # Нам нужны СТРОГО Смартфоны со статусом success. Всё остальное — в сторону!
        if p_type != "Смартфон" or status == "failed":
            continue

        # ШАГ 5: ШТАМПУЕМ ОБЪЕКТ КЛАССА, ПЕРЕДАВАЯ ИМЯ И ГРЯЗНУЮ ЦЕНУ
        smart = ElectronicsConverter(title, raw_price)

        # ШАГ 6: ЖМЕМ НА КНОПКУ МОДЕЛИ И ПОЛУЧАЕМ ЦЕНУ СО СКИДКОЙ
        discount_price = smart.get_discount_price()

        # Копим общую сумму в наш финтех-счётчик
        total_sum += discount_price

        print(f"📱 Модель: {smart.title} | Старая цена: {smart.price} руб. | Со скидкой: {discount_price} руб.")

    # ШАГ 7: ВЫВОДИМ ФИНАЛЬНЫЙ СУММАРНЫЙ ОТЧЁТ ДЛЯ АНАЛИТИКОВ
    print("\n-------------------------------------------------------------")
    print(f"💰 ОБЩАЯ СУММА УПУЩЕННОЙ ВЫГОДЫ (СО СКИДКОЙ 10%): {total_sum} руб.")
    print("-------------------------------------------------------------")


# ЗАПУСКАЕМ НАШУ СИСТЕМУ АВТОМАТИЗАЦИИ
process_electronics()
