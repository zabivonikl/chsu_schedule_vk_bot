from threading import Thread

from database import Database
from event_handler import EventHandler
from vk import Vk


def handle_event(event_obj):
    event_handler.handle_event(event_obj)


# TODO сделать рассылку
if __name__ == "__main__":
    vk = Vk()
    database = Database()
    event_handler = EventHandler(vk, database)
    while True:
        try:
            event = vk.listen_server()
            thread = Thread(target=handle_event, args=(event,))
            thread.start()
        except Exception as e:
            print(e)
