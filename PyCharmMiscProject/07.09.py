import csv
import psycopg
# Тут мы посмотрим 1ю строчку с данными что бы не грузить память. Потом закоментируем.
with open("retail_store_sales.csv", mode = "r", encoding = "utf-8") as file:
    reader = csv.reader(file)
    # 1.Тут будут названия колонок
    """header = next(reader)
    print("Названия колонок в файле:", header)
    # 2.Тут будет первая строка
    first_row = next(reader)
    print("Состав первой строки:", first_row)"""
    next(reader) # Пропустим название колонки
    file_rows = list(reader)

# Класс очистки
class Filter:
    def __init__(self, id_transaction, id_customer, category, items, unit_price,
                 quantity, total_spent, pay_method, location, tr_date, dis_applied):
        self.id_transaction = id_transaction.strip()
        self.id_customer = int(id_customer.split("_")[-1]) # Оставляем уникальный номер
        self.category = category.strip()
        if not items.strip() :
            self.items = "Not Items" # Если в строке пусто, пишем нет товара
        else:
            self.items = items.strip()
        if not unit_price.strip(): # Если в строке что то есть, убираем пробелы. идем дальше
            if not quantity.strip() or not total_spent.strip(): # Проверяем наличе данных в строках влияющих на начальную
                self.unit_price = 0 # Если в какой либ строке пусто, то присваиваем переменной "0"
            else: # Если строки не пустые, то переводим их во float и защищаем от деления на "0"
                new_quantity = float(quantity)
                new_total_spent = float(total_spent)
                if new_quantity > 0 and new_total_spent > 0:
                    self.unit_price = round(new_total_spent / new_quantity, 2) # Получаем нужное нам число, округленное до 2 знаков
                else: # Если сработала защита, то присваиваем переменной "0"
                    self.unit_price = 0
        else: # Иначе переводим строку во float
            self.unit_price = float(unit_price.strip())
        if not quantity.strip(): # Те же действия, что и ранее, только с получением второго значения
            if not unit_price.strip() or not total_spent.strip():
                self.quantity = 0
            else:
                new_unit_price = float(unit_price)
                new_total_spent = float(total_spent)
                if new_unit_price >0 and new_total_spent > 0:
                    self.quantity = float(new_total_spent / new_unit_price)
                else:
                    self.quantity = 0
        else:
            self.quantity = float(quantity.strip())
        if not total_spent.strip(): # Те же действия, что и ранее, только с получением второго значения
            if not unit_price.strip() or not quantity.strip():
                self.total_spent = 0
            else:
                new_unit_price = float(unit_price)
                new_quantity = float(quantity)
                if new_unit_price > 0 and new_quantity > 0:
                    self.total_spent = round(new_quantity * new_unit_price, 2)
                else:
                    self.total_spent = 0
        else:
            self.total_spent = float(total_spent.strip())
        if not pay_method.strip(): # Фильтр по типу оплаты, если нет - значит не известно.
            self.pay_method = "No Payment Method"
        else:
            pay_method = pay_method.strip().lower()
            if pay_method == "cash" or pay_method == "credit card":
                self.pay_method = pay_method
            else:
                self.pay_method = "Not defined"
        if not location.strip(): # Фильтр по местоположению, если нет - значит не известно.
            self.location = "No Location"
        else:
            location = location.strip().lower()
            if location == "in-store" or location == "online":
                self.location = location
            else:
                self.location = "Not defined"

        self.tr_date = tr_date.strip() # Просто убрал пробелы
        if dis_applied.strip().lower() in ["true"]: # Все что кроме "True" - без скидки.
            self.dis_applied = "Discount applied"
        else:
            self.dis_applied = "No discount"
    def return_filter(self): # Возвращаем отфильтрованную таблицу.
        print(self.id_transaction, self.id_customer, self.category, self.items, self.unit_price, self.quantity, self.total_spent, self.pay_method, self.location, self.tr_date, self.dis_applied)
        return self.id_transaction, self.id_customer, self.category, self.items, self.unit_price, self.quantity, self.total_spent, self.pay_method, self.location, self.tr_date, self.dis_applied

# Подключаемся к нашей базе, создаем и записываем таблицу
class Connect:
    def __init__(self):
        self.connection = psycopg.connect(
            dbname = "postgres", user = "postgres", password = "password", host = "127.0.0.1", port = "5432"
        )
        self.cursor = self.connection.cursor()
    def my_file(self):
        query = """
            create table if not exists retail_store_sales(
                id serial primary key,
                id_transaction varchar(100),
                id_customer varchar(100),
                category varchar(100),
                items varchar(50),
                unit_price float,
                quantity int,
                total_spent float,
                pay_method varchar(50),
                location varchar(50),
                tr_date varchar(50),
                dis_applied varchar(50)
                );
            """
        self.cursor.execute(query)
    def s_file(self, save):
        query = """
            insert into retail_store_sales (Id_Transaction, Id_Customer,
                Category, Items, Unit_Price, Quantity, Total_Spent, Pay_Method, 
                Location, Tr_Date, Dis_Applied)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(query, save)
    def disconnect(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        print("-----Таблица успешно записана----")
# Соединяем все вместе
def total_table():
    table = []
    for row in file_rows:
        id_transaction, id_customer, category, items, unit_price, quantity, total_spent, pay_method, location, tr_date, dis_applied = row
        new_table = Filter(id_transaction, id_customer, category, items, unit_price, quantity, total_spent, pay_method, location, tr_date, dis_applied)
        new_table = new_table.return_filter()
        table.append(new_table)
        print(table[0])
    return table

# Включаем

# Создаем переменную и присваиваем ей функцию очистки и записи чистого списка
new_total_table = total_table()
# Создаем объект класса подключения к базе
ct = Connect()
# Вызываем метод у созданного подключения для создания таблицы
ct.my_file()
# Показываем красиво сколько строк очищено
print(f"Очищено {len(new_total_table)} строк!")
# Берем по одной строке и передаем в функцию записи таблицы
for i in new_total_table:
    ct.s_file(i)
# Закрываем соединение
ct.disconnect()








