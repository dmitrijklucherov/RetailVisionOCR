import psycopg2

# 1. СЛОВАРЬ (Грязные данные от поставщика WB/Ozon на входе)
raw_goods = [
    {"name": "  Наушники ", "art": "  WB-101-AA ", "cost": " 4200 руб. "},
    {"name": " Мышка  ", "art": "OZ- 202 - BB", "cost": " 1500 "},
    {"name": " Клавиатура ", "art": "WB - 303 - CC   ", "cost": " 25000 руб. "}
]


# 2. КЛАСС (Робот-калибратор. Вся логика зачистки упакована внутри прибора)
class ProductConverter:
    def __init__(self, data_dict):
        # На лету чистим имя, артикул и цену, припаивая их через self к корпусу!
        self.title = data_dict["name"].strip()
        self.article = data_dict["art"].strip().replace("-", "").replace(" ", "")

        clean_money = data_dict["cost"].replace(" руб.", "").strip()
        self.price = int(clean_money)

    # Встроенная кнопка прибора для выдачи ровного кортежа для SQL
    def get_tuple(self):
        return (self.title, self.article, self.price)


# 3. ФУНКЦИЯ-УПРАВЛЕНЕЦ (Связывает конвейер с базой данных)
def start_etl_pipeline(items_list):
    # Открываем вентиль связи с PostgreSQL
    connection = psycopg2.connect(
        dbname="postgres", user="postgres", password="flashka57rus", host="127.0.0.1", port="5432"
    )
    cursor = connection.cursor()

    # 4. ЦИКЛ (Транспортёрная лента)
    for row in items_list:
        # Шаг А: Засыпаем грязный СЛОВАРЬ внутрь КЛАССА. Робот мгновенно штампует чистый объект!
        clean_item = ProductConverter(row)

        # Шаг Б: Жмём на кнопку прибора и забираем чистый кортеж прямо для SQL-пазов!
        sql_data = clean_item.get_tuple()

        # Шаг В: Мгновенно отправляем данные по трубе в PostgreSQL
        insert_query = """
            INSERT INTO oop_marketplace_products (title, article, price_rub)
            VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, sql_data)  # Передали готовый чистый кортеж!
        print(f"Товар '{clean_item.title}' успешно упакован в ООП и записан в СУБД!")

    # Фиксируем данные на диске и закрываем вентили
    connection.commit()
    cursor.close()
    connection.close()
    print("\n--- СВЯЗКА СЛОВАРЬ -> ЦИКЛ -> КЛАСС -> БАЗА СРАБОТАЛА ИДЕАЛЬНО! ---")


# ПУСК КОНВЕЙЕРА
start_etl_pipeline(raw_goods)
