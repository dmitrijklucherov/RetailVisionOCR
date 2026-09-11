import psycopg2

# 1. Подключаемся к базе данных
connection = psycopg2.connect(
    host="127.0.0.1",  # Числами, чтобы не было ошибок кодировки
    database="postgres",
    user="postgres",
    password="flashka57rus",
    port="5432",
)

# 2. Создаем курсор для выполнения команд
cursor = connection.cursor()

# 3. Делаем запрос
cursor.execute("SELECT version();")
print(cursor.fetchone())

# 4. Обязательно закрываем за собой соединение
cursor.close()
connection.close()

