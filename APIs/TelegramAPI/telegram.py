from time import sleep

import requests

from APIs.TelegramAPI.telegram_keyboard import TelegramKeyboard


class Telegram:
    def __init__(self, token=None):
        self.__bot_link = f"https://api.telegram.org/bot{token}/"
        self.__check_connection()
        self.__last_update = ""
        self.__event = None
        self.__init_last_update()

    def __check_connection(self):
        me_info = self.get_me()
        if not me_info['ok']:
            raise ConnectionError(f"Telegram API: {me_info['description']}")

    def get_me(self):
        return self.__call_method("getMe")

    @staticmethod
    def get_api_name():
        return "telegram"

    @staticmethod
    def get_admins():
        return [672743407]

    @staticmethod
    def get_standard_keyboard():
        kb = TelegramKeyboard()
        kb.add_line()
        kb.add_button("Расписание на сегодня")
        kb.add_button("Расписание на завтра")
        kb.add_line()
        kb.add_button("Расписание на другой день")
        kb.add_line()
        kb.add_button("Рассылка")
        kb.add_button("Изменить группу")
        return kb.get_keyboard()

    @staticmethod
    def get_start_keyboard():
        kb = TelegramKeyboard()
        kb.add_line()
        kb.add_button("Студент")
        kb.add_button("Преподаватель")
        return kb.get_keyboard()

    @staticmethod
    def get_empty_keyboard():
        return None

    def listen_server(self):
        while True:
            self.__get_event()
            if self.__is_new_last_id():
                return self.__update_last_id_and_get_event()

    def __get_event(self):
        self.__event = self.__call_method("getUpdates", {"offset": self.__last_update})

    def __call_method(self, method_name, params=None):
        try:
            return requests.get(self.__bot_link + method_name, params=params).json()
        except Exception as e:
            print(e)
            sleep(5)

    def __init_last_update(self):
        self.__get_event()
        self.__last_update = self.__event['result'][len(self.__event['result']) - 1]['update_id']

    def __is_new_last_id(self):
        return self.__last_update != self.__event['result'][len(self.__event['result']) - 1]['update_id']

    def __update_last_id_and_get_event(self):
        self.__last_update = self.__event['result'][len(self.__event['result']) - 1]['update_id']
        last_event = self.__event['result'][len(self.__event['result']) - 1]
        if 'text' in last_event['message']:
            return {
                "from_id": last_event['message']['from']['id'],
                "text": last_event['message']['text']
            }

    def send_message_queue(self, queue, peer_ids, keyboard):
        for element in queue:
            self.send_message(element, peer_ids, keyboard)

    def send_message(self, message, peer_ids, keyboard=None):
        for peer_id in peer_ids:
            params = {
                "chat_id": peer_id,
                "text": message,
                "reply_markup": keyboard
            }
            self.__call_method("sendMessage", params)
