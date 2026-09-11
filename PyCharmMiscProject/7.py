truck_fleet = [
    {"driver": "Иванов", "truck": "КАМАЗ", "fuel_spent": 450, "status": "В рейсе"},
    {"driver": "Матвеев", "truck": "МАЗ", "fuel_spent": 310, "status": "Ремонт двигателя"},
    {"driver": "Иванов", "truck": "КАМАЗ", "fuel_spent": 580, "status": "В рейсе"},
    {"driver": "Петрович", "truck": "ГАЗель", "fuel_spent": 90, "status": "Ремонт подвески"}
]
def generate_fleet_report(fleet_list):
    in_trip_count = 0
    in_repair_count = 0
    total_fuel = 0
    for truck in fleet_list:
        total_fuel += truck["fuel_spent"]
        if truck["status"] == "В рейсе":
            in_trip_count += 1
        elif "Ремонт" in truck["status"]:
            in_repair_count += 1
    report = {
        "в_рейсе": in_trip_count,
        "в_ремонте": in_repair_count,
        "всего_топлива": total_fuel
    }
    return report
print(generate_fleet_report(truck_fleet))
