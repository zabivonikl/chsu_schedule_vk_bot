from datetime import datetime, timedelta
from json import loads
from random import randint
from re import match
from sqlite3 import connect
from threading import Thread

from requests import get, exceptions
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard

from id_lists import *
from tokens import VK_API, GROUP_ID


def get_schedule(from_id, start_date, last_date=None):
    with connect('users.db') as conn:
        curs = conn.cursor()
        curs.execute(f"SELECT * FROM ids WHERE vk_id='{from_id}'")
        res = curs.fetchone()
    chsu_id = res[1]
    id_type = res[2]

    url = 'https://www.chsu.ru/raspisanie?p_p_id=TimeTable_WAR_TimeTableportlet&p_p_lifecycle=2&p_p_state=normal' \
          '&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1'
    payload = {
        "_TimeTable_WAR_TimeTableportlet_cmd": "timeTable",
        "_TimeTable_WAR_TimeTableportlet_typeTimeTable": "period",
        "_TimeTable_WAR_TimeTableportlet_group": chsu_id,
        "_TimeTable_WAR_TimeTableportlet_type": id_type,
        "_TimeTable_WAR_TimeTableportlet_startDate": start_date,
        "_TimeTable_WAR_TimeTableportlet_endDate": last_date or start_date,
        "_TimeTable_WAR_TimeTableportlet_professor": chsu_id
    }
    resp = get(url, params=payload)
    js = loads(resp.text)
    resp = []
    current_date = ""
    iterator = -1
    for elem in js:
        if current_date != elem['dateEvent']:
            current_date = elem['dateEvent']
            iterator += 1
            resp.append(f'\n=====Расписание на {current_date}=====\n')
        resp[iterator] += f"{elem['startTime']}-{elem['endTime']} {elem['dateEvent']}\n"
        resp[iterator] += f"{elem['abbrlessontype'] or ''}., {elem['discipline']['title']}\n"
        if id_type == 'student':
            for prof in elem['lecturers']:
                resp[iterator] += f"{prof['fio']}, "
        else:
            for group in elem['groups']:
                resp[iterator] += f"{group['title']}, "
        resp[iterator] = resp[iterator][:-2] + '\n'
        resp[iterator] += f"{elem['build']['title']}, аудитория {elem['auditory']['title']}\n" if elem['online'] == 0 \
            else "Онлайн\n"
        resp[iterator] += "\n"
    return resp or ["На текущий промежуток времени расписание не найдено\n"]


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
        domain = api.users.get(
            user_ids=event_obj['from_id'],
            fields='domain'
        )[0]['domain']
        api.messages.send(
            message=f"Сообщение от https://vk.com/{domain}: {event_obj['text'][1:]}",
            peer_id=447828812,
            random_id=randint(0, 4096),
            keyboard=default_kb.get_empty_keyboard()
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
            with connect('users.db') as conn:
                curs = conn.cursor()
                curs.execute(
                    f'''INSERT OR REPLACE INTO ids (vk_id, chsu_id, id_type) VALUES ({event_obj['from_id']}, {PROFESSORS[event_obj['text']]}, "professor")'''
                )
        elif event_obj['text'] in GROUPS:
            with connect('users.db') as conn:
                curs = conn.cursor()
                curs.execute(
                    f'''INSERT OR REPLACE INTO ids (vk_id, chsu_id, id_type) VALUES ({event_obj['from_id']}, {GROUPS[event_obj['text']]}, "student")'''
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
        if event_obj['text'].split('-')[0] > event_obj['text'].split('-')[1]:
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

    while True:
        try:
            for event in VkBotLongPoll(session, GROUP_ID).listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    thread = Thread(target=handle_event, args=(event.object,))
                    thread.start()
        except exceptions.ReadTimeout as e:
            print(f"Ошибка {e}")
