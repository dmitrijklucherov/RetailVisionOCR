raw_servers = [
    {"name": "Главный_шлюз", "ip": "http://192.168.1.1", "status": "online"},
    {"name": "База_данных", "ip": "10.0.0.5", "status": "offline"},
    {"name": "Диспетчерская", "ip": "https://172.16.0.4", "status": "online"}
]
def standardize_ip(ip_string):
    ip_string.strip()
    if ip_string.startswith("https://"):
        return ip_string
    elif ip_string.startswith("http://"):
        return ip_string.replace("http://", "https://")
    else:
        return f"https://{ip_string}"
def process_network(server_list):
    clean_network_report = []
    for server in server_list:
        secure_ip = standardize_ip(server["ip"])
        server_info ={
            "Сервер": server["name"],
            "Безопасный_ip": secure_ip,
            "Сеть": server["status"]
        }
        clean_network_report.append(server_info)
    return clean_network_report
print(process_network(raw_servers))
