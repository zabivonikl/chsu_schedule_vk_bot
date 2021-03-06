from datetime import datetime, timezone, timedelta
from threading import Thread
from time import sleep

from APIs.MongoDbAPI.mongo_db import MongoDB
from APIs.TelegramAPI.telegram import Telegram
from APIs.VkAPI.vk import Vk
from DataHandlers.event_handler import EventHandler
from tokens import TELEGRAM_API


def send_schedule(time):
    users = database.get_mailing_subscribers_by_time(time)
    for user in users:
        if user[1] == telegram_api.get_api_name():
            handle_telegram_event({
                "from_id": user[0],
                "text": "Расписание на завтра"
            })
        elif user[1] == vk_api.get_api_name():
            handle_vk_event({
                "from_id": user[0],
                "text": "Расписание на завтра"
            })


def start_mailing():
    while True:
        time = datetime.now(timezone(timedelta(hours=3.0))).strftime("%H:%M")
        try:
            sending = Thread(target=send_schedule, name=f'Sending at {time}', args=(time,))
            sending.start()
            sleep(1 * 60)
        except Exception as err:
            print(err)


def handle_vk_event(event_obj):
    try:
        EventHandler(vk_api, database).handle_event(event_obj)
    except Exception as err:
        print(err)


def listen_vk_server():
    while True:
        try:
            event = vk_api.listen_server()
            vk_event_handling = Thread(target=handle_vk_event, args=(event,))
            vk_event_handling.start()
        except Exception as err:
            print(err)


def handle_telegram_event(event_obj):
    try:
        EventHandler(telegram_api, database).handle_event(event_obj)
    except Exception as err:
        print(err)


def listen_telegram_server():
    while True:
        event = telegram_api.listen_server()
        tg_event_handling = Thread(target=handle_telegram_event, args=(event,))
        tg_event_handling.start()


if __name__ == "__main__":
    database = MongoDB()
    vk_api = Vk()
    telegram_api = Telegram(TELEGRAM_API)

    try:
        vk_bot = Thread(target=listen_vk_server, name="VKBotProcess")
        tg_bot = Thread(target=listen_telegram_server, name="TelegramBotProcess")
        mailing = Thread(target=start_mailing, name="MailingProcess")

        print("Starting vk-bot...")
        vk_bot.start()
        print("Starting telegram-bot...")
        tg_bot.start()
        print("Starting mailing...")
        mailing.start()
        print("Done!")
    except Exception as e:
        print(e)
