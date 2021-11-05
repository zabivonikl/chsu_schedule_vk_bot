from random import randint

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard

import tokens as tokens


class Vk:
    def __init__(self):
        self.__session = VkApi(token=tokens.VK_API, client_secret=tokens.VK_API)
        self.__api = self.__session.get_api()

    @staticmethod
    def get_admins():
        return [447828812, 284737850, 113688146]

    @staticmethod
    def get_standard_keyboard():
        default_kb = VkKeyboard(one_time=False, inline=False)
        default_kb.add_button(
            label="Расписание на сегодня",
            color="primary"
        )
        default_kb.add_button(
            label="Расписание на завтра",
            color="secondary"
        )
        default_kb.add_line()
        default_kb.add_button(
            label="Расписание на другой день",
            color="secondary"
        )
        default_kb.add_line()
        default_kb.add_button(
            label="Рассылка",
            color="positive"
        )
        default_kb.add_button(
            label="Изменить группу",
            color="negative"
        )
        return default_kb.get_keyboard()

    @staticmethod
    def get_start_keyboard():
        start_kb = VkKeyboard(one_time=False, inline=True)
        start_kb.add_button(
            label="Преподаватель",
            color="primary"
        )
        start_kb.add_line()
        start_kb.add_button(
            label="Студент",
            color="primary"
        )
        return start_kb.get_keyboard()

    @staticmethod
    def get_empty_keyboard():
        return VkKeyboard.get_empty_keyboard()

    @staticmethod
    def get_api_name():
        return "vk"

    def send_message_queue(self, queue, peer_ids, keyboard):
        for element in queue:
            self.send_message(element, peer_ids, keyboard)

    def send_message(self, message, peer_ids, keyboard):
        self.__api.messages.send(
            message=message,
            peer_ids=peer_ids,
            random_id=randint(0, 4096),
            keyboard=keyboard
        )

    def listen_server(self):
        for event in VkBotLongPoll(self.__session, tokens.GROUP_ID).listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                return event.object
