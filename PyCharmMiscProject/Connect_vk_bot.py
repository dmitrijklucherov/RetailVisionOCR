# Скритп №1. Создан 10.09.26 в 23-35
import os
from dotenv import load_dotenv
import vk_api
            # Из библиотеки импортируем: приемник сообщений и определитель типа
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
load_dotenv()
TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = "125630665"

def start_bot():
    vk_session = vk_api.VkApi(token = TOKEN)
    # Открываем канал связи
    longpoll = VkBotLongPoll(vk_session, group_id = GROUP_ID)
    print("Подключенние установлеено!")
    # Запуск бесконечного цикла перехвата входящих сообщений
    for event_vk in longpoll.listen():
        # Если сообщенеи то заходим:
       if event_vk.type  == VkBotEventType.MESSAGE_NEW:
           # Находит в потоке данных только сообщение /// Есть другой вариант, пока этот менее подвержен ошибкам - но чуть медленее
           vk_message_object = event_vk.raw.get('object', {}).get('message', {})
           # Либо текст, либо пусто
           vk_user_message = vk_message_object.get('text', 0)
           # ID пользователя, либо 0
           vk_user_id = vk_message_object.get('from_id', 0)
           # Проверка подлинности данных (именно текст)
           if vk_user_message:
               print(f"Бот прочитал текст: {vk_user_message}")
           else:
               print(f"Пользователь {vk_user_id} прислал не текст!")
# Защита от случайного зависания
if __name__ == "__main__":
    start_bot()




