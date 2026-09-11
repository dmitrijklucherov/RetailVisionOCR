import psycopg
# Подключаемся
def connect():
    connection = psycopg.connect(
        dbname = "postgres", user = "postgres", password = "password", host = "127.0.0.1", port = "5432"
    )
    cursor = connection.cursor()
    # Удаляем столбец в таблице ( Изменить "ИМЯ_ТАБЛИЦЫ" и сбросить "КОЛОНКУ")
    query_drop = """
        alter table my_file drop column rank_num; 
    """
    cursor.execute(query_drop) # Перенос данных в базу
    connection.commit() # Сохраняем изменения ( иначе все останется в буфере и не схранится)
    # Забираем одну строчку для проверки
    query_examination = """
        select * from my_file limit 1;
        """
    # Выполняем действие
    cursor.execute(query_examination)
    print(cursor.description)
    cursor.close()
    connection.close()
connect()