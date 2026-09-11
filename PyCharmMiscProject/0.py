class Truck:
    def __init__(self, driver_name, truck_model, raw_price):
        self.driver = driver_name.strip()
        self.model = truck_model
        clean_money = raw_price.replace(" руб.", "").strip()
        self.price = int(clean_money)
        self.status = "Готов"
    def send_to_trip(self):
        self.status = "В рейсе"
    def get_sql_data(self):
        return(self.driver, self.model, self.price)
kamaz = Truck(" Иванов", "КАМАЗ", " 4500 руб.")
gazel = Truck(" Петрович", " ГАЗель ", " 1200 ")
print(f"Водитель 1: {kamaz.driver} | Цена: {kamaz.price} | Статус: {kamaz.status}")
print(f"Водитель 2: {gazel.driver} |Цена: {gazel.price} | Статус: {gazel.status}\n")
kamaz.send_to_trip()
print("---После нажатия кнопки---")
print(f"Статус камаза: {kamaz.status}")
print(f"Статус Газели: {gazel.status}")
print(f"\nДанные для SQL: {kamaz.get_sql_data()}")
