raw_refunds = [
    {"user": "id_44", "item_code": "  REF-909-X ", "cost": "4200 руб."},
    {"user": "id_12", "item_code": None, "cost": None},
    {"user": "id_44", "item_code": "OZ- 111 - Y", "cost": "1500 руб."},
    {"user": "id_88", "item_code": "  WB - 333 - Z   ", "cost": "800 руб."},
    {"user": "id_00", "item_code": "TEST_ERROR", "cost": "0 руб."}
]


# ЦЕХ 1: Принимает ОДИН грязный словарь, возвращает ОЧИЩЕННЫЙ словарь
def clean_single_refund(refund_dict):
    # 1. Если внутри None — бракуем, возвращаем None
    if refund_dict["item_code"] is None or refund_dict["cost"] is None:
        return None

    # 2. Очищаем стоимость. Убираем " руб.", пробелы и переводим в int
    raw_cost = refund_dict["cost"].replace(" руб.", "").strip()
    clean_cost = int(raw_cost)

    # 3. Если стоимость 0 — бракуем тестовый лог
    if clean_cost == 0:
        return None

    # 4. Очищаем код товара от пробелов и дефисов
    clean_code = refund_dict["item_code"].strip().replace("-", "").replace(" ", "")

    # 5. Собираем красивую чистую карточку обратно
    return {
        "user": refund_dict["user"],
        "item_code": clean_code,
        "cost": clean_cost
    }


# ЦЕХ 2: Главный конвейер. Крутит цикл по СПИСКУ
def process_all_refunds(refunds_list):
    clean_data_box = []  # Сюда складываем чистые словари
    total_loss = 0
    count = 0

    for item in refunds_list:
        # Отправляем карточку в мелкий цех
        cleaned_item = clean_single_refund(item)

        # Если мелкий цех вернул None (отбраковал) — пропускаем круг
        if cleaned_item is None:
            continue

        # Накапливаем аналитику по успешным чистым картам
        clean_data_box.append(cleaned_item)
        total_loss += cleaned_item["cost"]
        count += 1

    # Собираем финальный отчет для бизнеса
    return {
        "total_loss": total_loss,
        "count": count,
        "clean_data": clean_data_box
    }


print(process_all_refunds(raw_refunds))
