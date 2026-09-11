truck_fleet = [
    {"driver": "Иванов", "truck": "КАМАЗ", "mileage": 1200},
    {"driver": "Матвеев", "truck": "МАЗ", "mileage": 800},
    {"driver": "Петров", "truck": "ГАЗель", "mileage": 450}
]
def find_overmileage(fleet_list, max_limit):
    over_box =[]
    for truck in fleet_list:
        if truck["mileage"] > max_limit:
            over_box.append(truck["driver"])
    return over_box
print(find_overmileage(truck_fleet, 1000))
