import psycopg2
simple_trucks = [
    {"driver": "Иванов", "model": "КАМАЗ"},
    {"driver": "Петрович", "model": "ГАЗель"},
    {"driver": "Сергеев", "model": "Scania"}
]
def upload_simple_fleet(fleet_list):
    # Создали функцию, открывае соединение
    connection = psycopg2.connect(
        dbname = "postgres",
        user = "postgres",
        password = "flashka57rus",
        host = "127.0.0.1",
        port = "5432"
    )
    cursor = connection.cursor()
    print("--- Мост открыт ---")
    for car in fleet_list:
        name = car["driver"]
        truck = car["model"]
        insert_query = """
            insert into simpl_fleet_logs(driver_name, truck_model)
            values (%s, %s);
        """
        cursor.execute(insert_query, (name,truck))
        print(f"Водитель{name}, уехал на автомобиле {truck}")
    connection.commit()
    cursor.close()
    connection.close()
    print("\n --- Мост закрты ---")
upload_simple_fleet(simple_trucks)