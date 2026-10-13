import asyncio # Параллельное выполнение задч с задержками
import re # Регулярки для точного поиска
import easyocr # Распознование текста
from pydantic import BaseModel, Field # Контроль типов данных, с защитой от падения кода
from datetime import datetime # Реальное время для отображения времени запроса

# 1.Вызов функции realtime
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# 2. Модуль проверки качества считанного текста
    # Статус, id, цена, все остальное
class OCRResult(BaseModel):
    status: str
    sku_id: int = Field(0, description="Артикул товара")
    detected_price: int = Field(0, ge=0, description="Найденная цена в руб.")
    raw_text: str = Field(..., description="Весь остальной текст")
    check_time: str = Field(default_factory=get_time, description="Время записи в базу")
# 3. Ассинхронная функция компьютерного зрения
async def recognize_price_tags(image_name):
    image_path = f"data/{image_name}" # Путь к скрину
    try:
        # Задаём языки чтения и место - процессор ПК
        reader = easyocr.Reader(['ru', 'en'], gpu=False)
        # Считываем текст с картинки с настройками: скрин, метод распознования, кол-во цепочек распознования,
        # увеличение контрасности, собираем только чистый текст без координат рамок
        bounds = reader.readtext(image_path, decoder='greedy', beamWidth=8,
                                 adjust_contrast=True, detail=0)
        # Склеиваем строки через пробел
        full_raw_text = " ".join(bounds)
        # Ищем артикул и цену
        id_match = re.search(r'Артикул\b\D*(\d+)', full_raw_text, re.IGNORECASE)
        price_match = re.search(r'(\d+)\s*(?:руб|руб\.|₽|\bкоп\b)', full_raw_text, re.IGNORECASE)
        product_id = int(id_match.group(1)) if id_match else 0
        if price_match:
            detected_price = int(price_match.group(1))
            status = "success"
        else:
            # Если ценынет, то пробуем другой вариант
            numbers = re.findall(r'\d+', full_raw_text)
            detected_price = int(numbers[0]) if numbers else 0
            status = "success" if detected_price > 0 else "error"
    except Exception as e:
        print(f"Сбой ИИ, ошибка: {e}")
        product_id = 0
        detected_price = 0
        full_raw_text = str(e)
        status = "error"
    # Отправляем полученые данные в фильтр
    validated_data = OCRResult(
        status=status,
        sku_id=product_id,
        detected_price=detected_price,
        raw_text="Тут мы вызовем функцию которая находит название"
        )
    # Ворзвращаем данные в виде словаря
    return validated_data.model_dump()


# Центральный асинхронный пусковой пульт
async def main():
    # Название твоего тестового скриншота, который лежит в папке data
    test_image = "test.png"

    result = await recognize_price_tags(test_image)

    print(result)
    print("==================================================\n")


if __name__ == "__main__":
    # Запускаем Event Loop нашей новой настроенной кнопкой Run в PyCharm!
    asyncio.run(main())








