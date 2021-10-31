from threading import Thread

import TelegramBot.telegram
from MembersDataAndUniversityIds.database import Database
from VkBot.vk import Vk
from event_handler import EventHandler
from tokens import TELEGRAM_API


def handle_vk_event(event_obj):
    EventHandler(vk_api, database).handle_event(event_obj)


def listen_vk_server():
    while True:
        event = vk_api.listen_server()
        vk_event_handling = Thread(target=handle_vk_event, args=(event,))
        vk_event_handling.start()


def handle_telegram_event(event_obj):
    telegram_api.send_message(event_obj, [event_obj["from_id"]])


def listen_telegram_server():
    while True:
        event = telegram_api.listen_server()
        tg_event_handling = Thread(target=handle_telegram_event, args=(event,))
        tg_event_handling.start()


# TODO сделать рассылку
if __name__ == "__main__":
    database = Database()
    vk_api = Vk()
    telegram_api = TelegramBot.telegram.Telegram(TELEGRAM_API)
    try:
        vk_bot = Thread(target=listen_vk_server)
        tg_bot = Thread(target=listen_telegram_server)

        vk_bot.start()
        tg_bot.start()
    except Exception as e:
        print(e)
