from threading import Thread

from event_handler import EventHandler
from vk import Vk


def handle_event(event_obj):
    try:
        event_handler.handle_event(event_obj)
    except TypeError:
        api.messages.send(
            message="Ошибка ввода. Проверьте правильность ввода даты\n",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096)
        )


if __name__ == "__main__":
    vk = Vk()
    event_handler = EventHandler(vk)
    while True:
        try:
            event = vk.listen_server()
            thread = Thread(target=handle_event, args=(event,))
            thread.start()
        except Exception as e:
            print(e)
