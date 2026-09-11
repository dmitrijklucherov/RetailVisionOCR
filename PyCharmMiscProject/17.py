import psycopg2
# Подключение внешней библиотеки (драйвера), которая содержит
# скомпилированный код на C/Python для отправки сетевых пакетов
# на сервер СУБД PostgreSQL по протоколу TCP/IP [finance].
# Без этого импорта интерпретатор выдаст ошибку NameError, т
# ак как встроенных команд для работы с SQL в Python нет

def generate_big_db():
# Инициализация сетевого сокета и отправка авторизационного запроса на сервер
# СУБД.
    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="flashka57rus",
        host="127.0.0.1",
        port="5432"
    )
# Создание объекта управления транзакциями (курсора).
# Курсор необходим для инкапсуляции SQL-запросов, буферизации результатов, возвращаемых сервером,
# и отслеживания текущей позиции в результирующей выборке данных
    cursor = connection.cursor()
    print("---Мост с PstgreSQL открыт! Начинаем запись базы!")
    for i in range(1,101):
        if i%2 == 0:
            name = f"Смартфон модель {i}"
            art = f"OZON-{i*10}-XYZ"
            price = 15000 + (i*100)
            status = "success"
        else:
            name = f"Чехол Артикул {i}"
            art = f"WB-{i*5}-ABC"
            price = 300+(i*10)
            status = "failed"
        insert_query = """
            insert into big_marketplace_sales (product_name, article, price, status)
            values (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, art, price, status))
    connection.commit()
    cursor.close()
    connection.close()
    print("---Мост закрыт! 100 строк успешно добавлены!---")
generate_big_db()