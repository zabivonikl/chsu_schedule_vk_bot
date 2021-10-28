from datetime import datetime, timedelta
from random import randint
from re import match
from threading import Thread

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard

from database import Database
from id_lists import *
from site_schedule import SiteSchedule
from tokens import VK_API, GROUP_ID


def get_schedule(from_id, start_date, last_date=None):
    db_response = database.get_user_data(from_id)
    params = {
        "university_id": db_response["university_id"],
        "id_type": db_response["id_type"],
        "start_date": start_date,
        "last_date": last_date
    }
    return schedule.get_schedule_string_array(params)


def start(peer_id):
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(
        label="Преподаватель",
        color="primary"
    )
    kb.add_line()
    kb.add_button(
        label="Студент",
        color="primary"
    )
    api.messages.send(
        message="Кто вы?",
        peer_id=peer_id,
        random_id=randint(0, 4096),
        keyboard=kb.get_keyboard()
    )


def message_new(event_obj):
    if event_obj['text'] == 'Начать' or event_obj['text'] == "Изменить группу":
        start(event_obj['from_id'])
    elif event_obj['text'][0] == ';':
        api.messages.send(
            message=f"Сообщение в https://vk.com/gim207896794?sel={event_obj['from_id']}: {event_obj['text'][1:]}",
            peer_ids=[447828812, 284737850, 113688146],
            random_id=randint(0, 4096),
            keyboard=default_kb.get_keyboard()
        )
        api.messages.send(
            message=f"Сообщение отправлено",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096),
            keyboard=default_kb.get_keyboard()
        )
    elif event_obj['text'] == 'Преподаватель':
        api.messages.send(
            message="Введите ФИО",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096),
            keyboard=default_kb.get_empty_keyboard()
        )
    elif event_obj['text'] == 'Студент':
        api.messages.send(
            message="Введите номер группы",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096),
            keyboard=default_kb.get_empty_keyboard()
        )
    elif event_obj['text'] in GROUPS or event_obj['text'] in PROFESSORS:
        if event_obj['text'] in PROFESSORS:
            database.set_user_data(
                event_obj['from_id'],
                PROFESSORS[event_obj['text']],
                "professor"
            )
        elif event_obj['text'] in GROUPS:
            database.set_user_data(
                event_obj['from_id'],
                GROUPS[event_obj['text']],
                "student"
            )
        api.messages.send(
            message="Данные сохранены\n",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096),
            keyboard=default_kb.get_keyboard()
        )
    elif event_obj['text'] == "Расписание на сегодня":
        resp = get_schedule(
            event_obj['from_id'],
            f"{datetime.now().strftime('%d.%m.%Y')}"
        )
        for elem in resp:
            api.messages.send(
                message=elem,
                peer_id=event_obj['from_id'],
                random_id=randint(0, 4096),
                keyboard=default_kb.get_keyboard()
            )
    elif event_obj['text'] == "Расписание на завтра":
        resp = get_schedule(
            event_obj['from_id'],
            f"{(datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')}"
        )
        for elem in resp:
            api.messages.send(
                message=elem,
                peer_id=event_obj['from_id'],
                random_id=randint(0, 4096),
                keyboard=default_kb.get_keyboard()
            )
    elif event_obj['text'] == "Расписание на другой день":
        api.messages.send(
            message="Введите дату\n\nПример:\n28.02\n31.10-07.11",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096),
            keyboard=default_kb.get_empty_keyboard()
        )
    elif match(r'\d\d[.]\d\d[-]\d\d[.]\d\d', event_obj['text']):
        start_time = event_obj['text'].split('-')[0] + f".{datetime.now().year}"
        if event_obj['text'].split('-')[0][2:3] > event_obj['text'].split('-')[1][2:3]:
            end_time = event_obj['text'].split('-')[1] + f".{datetime.now().year + 1}"
        else:
            end_time = event_obj['text'].split('-')[1] + f".{datetime.now().year}"
        resp = get_schedule(
            event_obj['from_id'],
            start_time,
            end_time
        )
        for elem in resp:
            api.messages.send(
                message=elem,
                peer_id=event_obj['from_id'],
                random_id=randint(0, 4096),
                keyboard=default_kb.get_keyboard()
            )
    elif match(r'\d\d[.]\d\d', event_obj['text']):
        resp = get_schedule(
            event_obj['from_id'],
            event_obj['text'] + f".{datetime.now().year}"
        )
        for elem in resp:
            api.messages.send(
                message=elem,
                peer_id=event_obj['from_id'],
                random_id=randint(0, 4096),
                keyboard=default_kb.get_keyboard()
            )
    else:
        api.messages.send(
            message="Такой команды нет. Проверьте правильность ввода.",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096)
        )


def handle_event(event_obj):
    try:
        message_new(event_obj)
    except TypeError:
        api.messages.send(
            message="Ошибка ввода. Проверьте правильность ввода даты\n",
            peer_id=event_obj['from_id'],
            random_id=randint(0, 4096)
        )


if __name__ == "__main__":
    session = VkApi(token=VK_API, client_secret=VK_API)
    api = session.get_api()

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
        label="Изменить группу",
        color="negative"
    )

    database = Database()
    schedule = SiteSchedule()
    while True:
        try:
            for event in VkBotLongPoll(session, GROUP_ID).listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    thread = Thread(target=handle_event, args=(event.object,))
                    thread.start()
        except Exception as e:
            print(e)
