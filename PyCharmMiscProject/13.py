# Задание 1
weights_data = [12.5, 24.1, 18.9, 32.0, 15.3, 20.0, 21.5]
def weigts(cars):
    car = []
    heavy_car = []
    for weight in cars:
        if weight < 20.0:
            car.append(weight)
        else:
            heavy_car.append(weight)
    print(f"Автомобили с перегрузом: {heavy_car}")
    return car
print(f"Автомобили без перегруза: {weigts(weights_data)}")
# На 1 задание ушло минут 15

# Задание 2
bad_articles = [
    {"product": "наушники", "art": "  WB-101-AA "},
    {"product": "мышка", "art": "OZ- 202 - BB"},
    {"product": "клавиатура", "art": "WB - 303 - CC   "}
]
def clean_items_db(raw_list):
    db = []
    for item in raw_list:
        items = item["art"].strip().replace("-", "").replace(" ", "")
        db.append(items)
    return db
print(f"Полученный список: {clean_items_db(bad_articles)}")
# На это задание ушло пол часа и пришлось воспользоваться подсказкой - поиском: метод удаления внутри, потому что strip() удаляет пробелы только по краям

# Задание 3
transactions_list = [
    {"id": 1, "amount": 3000, "status": "success"},
    {"id": 2, "amount": 5000, "status": "failed"},
    {"id": 3, "amount": 12000, "status": "success"},
    {"id": 4, "amount": 1500, "status": "success"}
]
def get_financical_summary(payments):
    get = 0
    got = 0
    for list in payments:
        if list["status"] == "success":
            get += list["amount"]
            got += 1
    gat = get/got
    transaction_list = {
        "Общая сумма": get,
        "Средний чек": gat
    }
    return transaction_list
print(f"Итог: {get_financical_summary(transactions_list)}")
# На третью задачу ушло 20 минут, но я подсмотрел похожую, которую мы решали раньше

# Задание 4
network_nodes = [
    {"node": "Сервер 1", "link": "  http://192.168.1.1 "},
    {"node": "Сервер 2", "link": "https://10.0.0.5"},
    {"node": "Сервер 3", "link": "http://172.16.0.2  "}
]
def fix_adress(url):
    return url.strip().replace("http:", "https:")
def secure_network_log(nodes_list):
    clean_network_nodes =[]
    for nodes in nodes_list:
        clean_nodes = fix_adress(nodes["link"])
        nodes["link"] = clean_nodes
        clean_network_nodes.append(nodes)
    return clean_network_nodes
print(f"Очищенный список: {secure_network_log(network_nodes)}")
# В этой задаче я многое подсмотрел из предыдущих, была ошибка, но я ее бысто нешел.