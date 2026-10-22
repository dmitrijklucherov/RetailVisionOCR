import asyncio
import os
import selectors
import tracemalloc
from dotenv import load_dotenv
from vk_api import vk_api
# Из библиотеки импортируем: приемник сообщений и определитель типа
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
# Импортируем защиту от повторов
from vk_api.utils import get_random_id

from data_base import Database
from filter_message import Filter

load_dotenv()
TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")


async def start_bot():
    # global vk_message_object
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()

    # ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
    db = Database()
    await db.connect()

    # Открываем канал связи с ВК
    longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

    # Захватываем текущий асинхронный цикл событий для выполнения отправки сообщений в потоке
    loop = asyncio.get_running_loop()

    # Запускаем бесконечный цикл перехвата входящих сообщений
    while True:
        try:
            events = longpoll.listen()
            for event_vk in events:
                # Если сообщение есть, то безопасно распаковываем его для отправки на анализ
                if event_vk.type == VkBotEventType.MESSAGE_NEW:
                    vk_message_object = event_vk.raw.get("object", {}).get("message", {})
                    vk_user_message = vk_message_object.get("text", "")
                    vk_peer_id = vk_message_object.get("peer_id", 0)
                    # Если нет текста в соообщении, проверяем упаковку ВК
                    if not vk_user_message:
                        attachments = vk_message_object.get("attachment", [])
                        for attach in attachments:
                            if attach.get("type") == "link":
                                vk_user_message = attach.get("link", {}).get("url", "")
                    # Если сообщения нет - пропускаем
                    if not vk_user_message:
                        continue
                    # Отправляем сообщение на анализ
                    action = await Filter.clean_message(vk_user_message, db_connection=db)
                    # Пока пропускаем спец-команды
                    if action.command == "!!!":
                        continue
                    # Проверяем что список артикулов не пустой
                    analytics = None
                    # Проверяем, что список артикулов не пустой
                    if action.product_id:
                        # 🎯 ИСПРАВЛЕНИЕ: Берем первое число из списка, а не весь список со скобками!
                        target_sku = action.product_id[0]

                        month_limit = action.days_depth if (action.days_depth and action.days_depth > 0) else 1
                        analytics = await db.get_product_analytics_data(str(target_sku), month_limit)

                    # Вызываем асингую модель ответа, передавая полученные данные
                    report_text = await action.get_report_text(db=db, analytics=analytics)
                    await loop.run_in_executor(
                        None,
                        lambda: vk.messages.send(
                            peer_id=vk_peer_id,
                            message=report_text,
                            random_id=get_random_id(),
                        ),
                    )
        except Exception as e:
            print(f"Сбой! Перезапуск: {repr(e)}")
            # print(vk_message_object)
            await asyncio.sleep(3)


async def main():
    await start_bot()


if __name__ == "__main__":
    # Включаем отслеживание асинхронных задач
    tracemalloc.start()

    # Безопасный пуск асинхронного движка на Windows без блокировок
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )