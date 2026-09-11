payments_log = [
    {"id": 1, "amount": 5000, "user": "Иван"},
    {"id": 2, "amount": -150, "user": "Тест_Бот"},
    {"id": 3, "amount": 0, "user": "Ошибка_Системы"},
    {"id": 4, "amount": 12000, "user": "Петрович"},
    {"id": 5, "amount": 3000, "user": "Сергей"}
]
def analyze_payments(transactions_list):
    clean_total_sum = 0
    good_payments_count = 0
    for pay in transactions_list:
        if pay["amount"] <= 0:
            continue
        else:
            clean_total_sum += pay["amount"]
            good_payments_count += 1
    average_check = clean_total_sum / good_payments_count
    average_check = round(average_check, 2)
    final_count = {
        "Общая сумма": clean_total_sum,
        "Средний чек": average_check
    }
    return final_count
print(analyze_payments(payments_log))