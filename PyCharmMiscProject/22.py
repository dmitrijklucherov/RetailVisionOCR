import psycopg2
# Подключаем библиотеку postgreSQL
gateway_transactions = [
    {"tx_id": "TX_991", "amount": " 50.50 USD ", "status": "success"},
    {"tx_id": "TX_992", "amount": "0.00 RUB", "status": "test"},
    {"tx_id": "TX_993", "amount": "2400.00 RUB", "status": "success"},
    {"tx_id": "TX_994", "amount": " 10.00 USD ", "status": "failed"}
]
# Создан список словарей - массив
# Создаем функцию для связи с postgresSQL
def process_fintech_payroll(transactions_list):
    connection = psycopg2.connect(
        dbname = "postgres",
        user = "postgres",
        password = "flashka57rus",
        host = "127.0.0.1",
        port = "5432"
    )
    # Настройка соединения
    cursor = connection.cursor()
    print("---Мост с базой данных открыт---\n")
    for tx in transactions_list:
    # Запускаем цикл по списку словарей и проверяем статус по ключу внутри
        if tx["status"] == "test" or tx["status"] == "failed":
            print(f"Транзакция {tx['tx_id']} отбракована. Статутс: {tx['status']}")
            continue
        # Уходим на следующий круг
        raw_money_text = tx["amount"]
        # Присваиваем значение ключа переменной и очищаем переменную от мусора
        clean_text = raw_money_text.replace("USD", "").replace("RUB", "").strip()
        # Переводим очищенный текст во float
        price_number = float(clean_text)
        # Находим значения в другой валюте и конвертируем их
        if "USD" in raw_money_text:
            price_number = price_number * 92.50
        # Округляем все полученные значенияи переводим в целое число
        final_rub_price = int(round(price_number))
        # Записываем очищенные данные в таблицу postgreSQL
        insert_query = """
        insert into new_day30 (tx_id, amount, status)
        values (%s,%s,%s)
        """
        cursor.execute(insert_query, (tx["tx_id"], final_rub_price, tx["status"]))
        print(f"Транзакция {tx['tx_id']} успешно записана в БД. Сумма {final_rub_price} руб.")
    connection.commit()
    cursor.close()
    connection.close()
    print("\n --- ELT-Процесс завершен. Все чистые данные нна складе базы данных!---")
process_fintech_payroll(gateway_transactions)


