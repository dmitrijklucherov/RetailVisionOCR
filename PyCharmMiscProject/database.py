import psycopg

class WBDatabase:
    def __init__(self):
    # Устанавливае соединение
        self.connection = psycopg.connect(
            dbname = "postgres", user = "postgres", password = "password", host = "127.0.0.1", port = "5432"
        )
        self.cursor = self.connection.cursor()
        # Создаем таблицу в PostgreSQL
    def create_table(self):
        query = """
            create table if not exists wb_sales(
            id serial primary key,
            nm_id varchar(50), -- Артикул товара 
            title varchar(200), -- Название товара
            price float, -- Текущая цена
            quantity int, -- Остаток товара
            check_date varchar(50) -- Дата и время проверки
            );
            """
        self.cursor.execute(query)
        print("Скрипт №2: Таблица wb_sales создана/проверена.")
        # Записываем в нашу таблицу
    def insert_product(self, data):
        query = """
            insert into wb_sales (nm_id, title, price, quantity, check_date)
             values (%s,%s,%s,%s,%s);
        """
        self.cursor.execute(query, data)
        # Закрываем соединение
    def disconnect(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        print("Все изменения зафиксированы, соединение закрыто")
# Тест создания и записи кода
if __name__ == "__main__":
    db = WBDatabase()
    db.create_table()
    test_item = ("1234", "Тестовая футболка", 993.34, 45, "11-09-2026 23:43")
    db.insert_product(test_item)
    db.disconnect()




