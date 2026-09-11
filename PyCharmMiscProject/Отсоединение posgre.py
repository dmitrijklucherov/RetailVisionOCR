import psycopg2

# 1. Открываем дверь в базу. Как только код выйдет из этого блока, дверь закроется!
with psycopg2.connect(
    host="127.0.0.1",
    database="postgres",
    user="postgres",
    password="flashka57rus",
    port="5432",
) as connection:

    # 2. Берем инструмент (курсор) для работы внутри базы
    with connection.cursor() as cursor:

        # 3. Передаем команду базе данных
        cursor.execute("SELECT version();")

        # 4. Получаем ответ
        result = cursor.fetchone()
        print("Ответ от базы:", result)

        # Здесь работа с курсором закончена -> Python автоматически уничтожает курсор

# Код вышел из блока 'with' (отступы закончились) -> Python автоматически ЗАКРЫЛ соединение!
print("Двери успешно и безопасно закрыты.")
