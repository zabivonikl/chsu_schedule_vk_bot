from random import randint

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import VkBot.tokens as tokens


class Vk:
    def __init__(self):
        self.__session = VkApi(token=tokens.VK_API, client_secret=tokens.VK_API)
        self.__api = self.__session.get_api()

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
