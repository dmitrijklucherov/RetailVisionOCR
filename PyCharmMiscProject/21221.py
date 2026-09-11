import csv

# 1. Просто открываем файл и забираем строки
with open("my_file.csv", mode="r", encoding="utf-8") as file_handler:
    reader = csv.reader(file_handler)
    next(reader)  # Пропустили шапку
    file_rows = list(reader)

# 2. Вытаскиваем самую первую строчку данных
first_row = file_rows[0]

print("--- РЕЗУЛЬТАТЫ СУДЕБНОЙ ЭКСПЕРТИЗЫ ФАЙЛА ---")
print(f"Фактическое количество колонок: {len(first_row)} шт.")
print("\nВот как выглядят данные в строке (скопируйте это):")
print(first_row)
