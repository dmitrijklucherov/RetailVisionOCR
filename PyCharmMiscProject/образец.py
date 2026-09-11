import csv
import psycopg

# 1. ЧИТАЕМ ФАЙЛ (Остаётся без изменений)
with open("dirty_marketplace_data.csv", mode="r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)
    marketplace_rows = list(reader)


# 2. КЛАСС №1: РОБОТ-ОЧИСТИТЕЛЬ (Остаётся без изменений)
class MarketCleaner:
    def __init__(self, product_type, title, raw_price):
        self.product = product_type.lower()
        self.title = title.upper().strip()
        price = raw_price.replace(" руб.", "").replace("руб", "").replace(" ", "")
        self.price = int(price)

    def re_market(self):
        return self.product, self.title, self.price


# ШАГ 3: ФУНКЦИЯ-ФИЛЬТР БРАКА (Остаётся без изменений)
def cleaner():
    clean_warehouse = []
    for clean in marketplace_rows:
        _, product, title, price, status = clean
        if status == "failed" or status == "test":
            continue
        clean_market = MarketCleaner(product, title, price)
        market_clean = clean_market.re_market()
        clean_warehouse.append(market_clean)
    return clean_warehouse


# =====================================================================
# 🌟 ВКУСНАЯ ИНЖЕНЕРИЯ: КЛАСС ДЛЯ УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ (ООП + SQL)
# =====================================================================
class DatabaseManager:
    def __init__(self):
        # При штамповке прибора мост к PostgreSQL открывается автоматически!
        self.connection = psycopg.connect(
            dbname="postgres", user="postgres", password="flashka57rus", host="127.0.0.1", port="5432"
        )
        self.cursor = self.connection.cursor()

    def create_table(self):
        # Кнопка создания таблицы на корпусе прибора
        query = """
            CREATE TABLE IF NOT EXISTS new_cleaner_market (
                id SERIAL PRIMARY KEY,
                product_type VARCHAR(50),
                product_name VARCHAR(100),
                price INT
            );
        """
        self.cursor.execute(query)

    def save_product(self, clean_row):
        # Кнопка записи ОДНОГО чистого кортежа
        query = """
            INSERT INTO new_cleaner_market (product_type, product_name, price)
            VALUES (%s, %s, %s);
        """
        self.cursor.execute(query, clean_row)

    def close_all(self):
        # Кнопка полной консервации вентилей и фиксации данных на диске
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        print("--- ООП-УПРАВЛЕНЕЦ БАЗЫ: СЕССИЯ ЗАКРЫТА, ДАННЫЕ ЗАПЕЧАТАНЫ! ---")


# =====================================================================
# 🎮 ГЛАВНЫЙ ЗАПУСКНОЙ ПУЛЬТ НА САМОМ НИЗУ ФАЙЛА
# =====================================================================

# Шаг А: Запускаем очистку файла и получаем чистый список
clean_data = cleaner()

# Шаг Б: Штампуем прибор управления базой данных по нашему ООП-чертежу!
db = DatabaseManager()

# Шаг В: Жмём на кнопку создания таблицы
db.create_table()

print(f"--- НАЧИНАЕМ ЗАПИСЬ {len(clean_data)} ТОВАРОВ ЧЕРЕЗ ООП-УПРАВЛЕНЕЦ БАЗЫ ---")

# Шаг Г: Крутим цикл и просто нажимаем встроенную кнопку db.save_product!
for row in clean_data:
    db.save_product(row)  # Никаких cursor.execute внутри цикла! Чистая кнопка!

# Шаг Д: В самом конце глушим прибор одной командой
db.close_all()
