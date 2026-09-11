sales_data = [
    {"product": "Наушники", "price": "1500 руб."},
    {"product": "Мышка", "price": None},
    {"product": "Клавиатура", "price": " 3200 "},
    {"product": "Монитор", "price": "25000 руб."}
]
# Дан прайс, нужно его отфильтровать
# Создаем функцию-фильтр
def clean_sales_report(report_list):
    # Создаем список для накопления резултата
    clean_box = []
    for item in report_list:
        if item["price"] is None:
            continue
        raw_price = item["price"].replace(" руб.", "").strip()
        clean_price = int(raw_price)
        item["price"] = clean_price
        clean_box.append(item)
    return clean_box
print(clean_sales_report(sales_data))

