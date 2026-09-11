import csv
import psycopg
# Находим и открываем файл с диска, mode = "r" - строго для чтения, encoding = "utf-8" - кодировка
with open("dirty_marketplace_data.csv", mode = "r", encoding = "utf-8") as file:
    # Создается специальный объект для того что бы брать строчку за строчкой, а не весь файл
    reader = csv.reader(file)
    # Пропускаем первую строчку, которая не содержит данных, а является техническим заголовком
    next(reader)
    # Преобразуем полученные строки в список списков
    marketplace_rows = list(reader)
# Создаем класс очистки и возврата чистого кортежа
class MarketCleaner:
    def __init__(self, product_type, title, raw_price):
       self.product = product_type.lower()
       self.title = title.upper().strip()
       price = raw_price.replace(" руб.", "").replace(" ", "")
       self.price = int(price)
    def re_market(self):
        return self.product, self.title, self.price
# Создаем функцию - фильтр
def cleaner():
    clean_warehouse = []
    for clean in marketplace_rows:
        product, title, price, status = clean
        if status == "failed" or status == "test":
            continue
        clean_market = MarketCleaner(product, title, price)
        market_clean = clean_market.re_market()
        clean_warehouse.append(market_clean)
    return clean_warehouse
def connect(baza):
    connection = psycopg.connect(
        dbname = "postgres", user = "postgres", password = "flashka57rus", host = "127.0.0.1", port = "5432"
    )
    cursor = connection.cursor()
    for row in baza:
        type_art, art, price = row
        query_cleaner = """
            insert into new_cleaner_market (product_type, product_name, price)
            values (%s,%s,%s);
        """
        cursor.execute(query_cleaner, (type_art, art, price))
    connection.commit()
    cursor.close()
    connection.close()
    print("Все данные успешно загружены")
connect(cleaner())




