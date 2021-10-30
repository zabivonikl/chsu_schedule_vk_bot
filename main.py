from threading import Thread

from MembersDataAndUniversityIds.database import Database
from VkBot.event_handler import VkEventHandler
from VkBot.vk import Vk


def handle_event(event_obj):
    event_handler.handle_event(event_obj)


# TODO сделать рассылку
if __name__ == "__main__":
    vk = Vk()
    database = Database()
    event_handler = VkEventHandler(vk, database)
    while True:
        try:
            event = vk.listen_server()
            thread = Thread(target=handle_event, args=(event,))
            thread.start()
        except Exception as e:
            print(e)
