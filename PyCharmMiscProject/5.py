security_logs = [
    {"ip": "192.168.1.5", "action": "LOGIN", "status": "success"},
    {"ip": "10.0.0.12", "action": "BRUTE_FORCE", "status": "blocked"},
    {"ip": "172.16.0.4", "action": "PORT_SCAN", "status": "blocked"},
    {"ip": "192.168.1.9", "action": "BRUTE_FORCE", "status": "failed"}
]
def filter_incidents(log_list, target_action):
    incedent_ips =[]
    for log in log_list:
        if log["action"] == target_action:
            incedent_ips.append(log["ip"])
    return incedent_ips
print(filter_incidents(security_logs, "BRUTE_FORCE"))