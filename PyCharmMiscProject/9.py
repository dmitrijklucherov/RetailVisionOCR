dirty_fleet = [
    {"driver": "Иванов", "truck": " камаз "},
    {"driver": "Петрович", "truck": "газель  "},
    {"driver": "Сергеев", "truck": "  scania "}
]
def clean_truck_name(name):
    return name.strip().upper()
def fix_fleet_data(fleet_list):
    clean_box = []
    for item in fleet_list:
        beatiful_name = clean_truck_name(item["truck"])
        item["truck"] = beatiful_name
        clean_box.append(item)
    return clean_box
print(fix_fleet_data(dirty_fleet))