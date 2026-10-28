import os
import time
import logging
import requests
from dotenv import load_dotenv
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.exceptions import ApiError
# from filter_message import "Функция для передачи - строка 23"

load_dotenv()
TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Функция принимает сообщение, отправляет в другой файл и отвечает пользователю
def handle_event(event, vk):
    if event.type == VkBotEventType.MESSAGE_NEW:
        message = event.obj.message
        text = message['text']
        peer_id = message['peer_id']
        from_id = message['from_id']
        # Отправляем в filter_message, ждем анализ и отвечаем
        try:
            bot_reply = "filter_message"(text, peer_id)  # Тут должна быть функция из фильтра
            if bot_reply:
                vk.messages.send(
                    peer_id=peer_id,
                    message=bot_reply,
                    random_id=0
                )
                logging.info(f"Пользователь:{from_id}, сделал запрос{text}")
        # Ошибка №1: Проблемы со стороны VK API
        except ApiError as vk_error:
            error_code = vk_error.error.get('error_code')
            error_msg = vk_error.error.get('error_msg')
            logging.error(f"Ошибка VK API! Код:{error_code} для {peer_id}: {error_msg}")
            # Проверка на блокировку от пользователя
            if error_code == 901:
                logging.warning(f"Пользователь {peer_id} заблокировал сообщения от сообщества")
        # Ошибка №2: Проблемы с логикой бота, а так же уведомление в сообщении об этом
        except(ValueError, KeyError, TypeError) as code_error:
            logging.error(f"Проблемы с ботом! Ошибка: {code_error}")
            try:
                vk.messages.send(peer_id=peer_id, message="Извините, произошла внутренняя ошибка", random_id=0)
            # Ловим ошибки при отправке уведомления об ошибке
            except ApiError as send_error:
                logging.warning(f"Не удалось отправить юзеру {peer_id} сообщение об ошибке {send_error}")
            except requests.exceptions.RequestException as net_error:
                logging.warning(f"Сбой сети при попытке отправить сообщение об ошибке для {peer_id}: {net_error}")
# Функция бесконечного ожидания сообщенея
def start_bot():
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()

    while True:
        try:
            longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)
            for event in longpoll.listen():
                handle_event(event, vk)
        # Ошибка №1: Проблемы с соеденением
        except requests.exceptions.RequestException as net_error:
            logging.error(f"Ошибка сети: {net_error}")
            logging.info("Попытка переподключения через 5 сек...\n")
            time.sleep(5)
        # Ошибка №2: Сброс сессии
        except ApiError as vk_error:
            error_code = vk_error.error.get('error_code')
            error_msg = vk_error.error.get('error_msg')
            logging.error(f"\nОшибка! Код {error_code}: {error_msg}")
            logging.info("Перезагрузка через 5 сек")
            time.sleep(5)


# Настройка запуска с логированием в файл
if __name__ == "__main__":
    # Создаем папку для логов
    os.makedirs("logs", exit_ok=True)
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO, # Обычные рабочие события бота
        filename="logs/VKbot.log", # Файл, куда сохранять лог
        filemode="a", # Дописывать новое, не стирая старое
        format="%(asctime)s - [%(levelname)s] - %(message)s", # Формат даты и сообщения
        datefmt="%Y-%m-%d %H:%M:%S" # Формат времени
    )
    # Первая запись и запуск
    logging.info("---Скрипт бота запущен пользователем---")
    start_bot()