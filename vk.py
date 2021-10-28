from random import randint

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from tokens import VK_API, GROUP_ID


class Vk:
    def __init__(self):
        self.session = VkApi(token=VK_API, client_secret=VK_API)
        self.api = self.session.get_api()

    def send_message_queue(self, queue, peer_ids, keyboard):
        for element in queue:
            self.send_message(element, peer_ids, keyboard)

    def send_message(self, message, peer_ids, keyboard):
        self.api.messages.send(
            message=message,
            peer_ids=peer_ids,
            random_id=randint(0, 4096),
            keyboard=keyboard
        )

    def listen_server(self):
        for event in VkBotLongPoll(self.session, GROUP_ID).listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                return event.object
