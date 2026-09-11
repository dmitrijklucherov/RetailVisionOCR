dirty_clients = [
    {"name": "Алексей", "phone": " 8-999-111-22-33 "},
    {"name": "Дмитрий", "phone": "8 915 000 11 22"},
    {"name": "Михаил", "phone": "8-900-555-44-33  "}
]
def clean_phone_number(phone_string):
    return phone_string.strip().replace("-","").replace(" ","")
def process_crm_data(clients_list):
    clean_crm_report = []
    for client in clients_list:
        perfect_phone = clean_phone_number(client["phone"])
        client["phone"] = perfect_phone
        clean_crm_report.append(client)
    return clean_crm_report
print(process_crm_data(dirty_clients))


