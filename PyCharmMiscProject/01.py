import psycopg2

raw_fruits = [
    {"type": "Яблоко", "color": "  Зеленое ", "weight_g": 180, "status": "отлично"},
    {"type": "Банан", "color": "Желтый", "weight_g": 200, "status": "отлично"},
    {"type": "Яблоко", "color": " Красное  ", "weight_g": 150, "status": "гнилое"},
    {"type": "Яблоко", "color": "  Зеленое ", "weight_g": 220, "status": "хорошо"}
]
class Fruits:
    def __init__(self, color_fruit, weight_fruit, status_fruit):
        self.color = color_fruit.strip()
        self.weight = int(weight_fruit)
        self.status = status_fruit
    def sql_fruit(self):
        return(self.color, self.weight, self.status)
def connect_fruits(item_list):
    connection = psycopg2.connect(
        dbname = "postgres", user = "postgres", password = "flashka57rus", host = "127.0.0.1", port = "5432"
    )
    cursor = connection.cursor()
    while True:
        weight_apple = int(input("Яблоки какого минимального веса вас интересуют? Введите:"))
        if weight_apple < 50:
            print(f"Вес - {weight_apple} слишком мал. Таких яблок нет на складе")
            continue
        else:
            for row in item_list:
                if row["type"] != "Яблоко" or row["status"] == "гнилое" or row["weight_g"] < weight_apple :
                    continue
                cleen_fruits = Fruits(row["color"], row["weight_g"], row["status"])
                sql_fruits = cleen_fruits.sql_fruit()
                query_fruits = """
                    insert into fruits_apple(color, weight, status)
                    values (%s,%s,%s);
                """
                cursor.execute(query_fruits, sql_fruits)
                print(f"Товар: {cleen_fruits.color} яблоко успешно добавлен")
            connection.commit()
            cursor.close()
            connection.close()
        break
connect_fruits(raw_fruits)
