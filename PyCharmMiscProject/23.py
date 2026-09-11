import psycopg2


def network_scanner():
    while True:
        type_attack = input("Введите тип атаки (например, BRUTE_FORCE): ").strip()

        # 1. Защита от пустого ввода
        if type_attack == "" or type_attack is None:
            print("Пустой запрос! Введите тип атаки заново.\n")
            continue

        # 2. БЕЗ ЛИШНИХ УСЛОВИЙ: Если текст есть — сразу открываем мост к СУБД!
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="flashka57rus",  # Впишите свой пароль
            host="127.0.0.1",
            port="5432"
        )
        cursor = connection.cursor()

        select_query = """
            SELECT ip_address, network_status
            FROM cybersecurity_logs
            WHERE action_type = %s;
        """
        cursor.execute(select_query, (type_attack,))
        attacks = cursor.fetchall()

        # Сразу закрываем сокеты базы данных
        cursor.close()
        connection.close()

        # 3. Проверяем, нашел ли кладовщик хоть что-нибудь
        if not attacks:
            print(f"По запросу '{type_attack}' ничего не найдено. Попробуйте еще раз.\n")
            continue

        # 4. Распаковываем кортежи на понятные переменные
        print(f"\n--- РЕЗУЛЬТАТЫ СКАНЕРОВ ПО ТИПУ: {type_attack} ---")
        for row in attacks:
            ip, status = row  # Вытащили IP и статус из круглых скобок
            print(f"⚠️ Выявлен инцидент! Нарушитель: {ip} | Статус в сети: {status}")

        break  # Успешно всё вывели и завершаем работу


network_scanner()
