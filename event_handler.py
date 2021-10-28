from datetime import datetime, timedelta
from re import match

from vk_api.keyboard import VkKeyboard

from database import Database
from id_lists import GROUPS, PROFESSORS
from site_schedule import SiteSchedule


class EventHandler:
    def __init__(self, vk):
        self.vk = vk
        self.database = Database()
        self.schedule = SiteSchedule()

        self.__get_standard_keyboard()
        self.__get_start_keyboard()
        self.__get_empty_keyboard()

    def __get_standard_keyboard(self):
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
        self.default_kb = default_kb.get_keyboard()

    def __get_start_keyboard(self):
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
        self.start_kb = start_kb.get_keyboard()

    def __get_empty_keyboard(self):
        self.empty_kb = VkKeyboard.get_empty_keyboard()

    def handle_event(self, event_obj):
        from_id = event_obj['from_id']
        if event_obj['text'] == 'Начать' or event_obj['text'] == "Изменить группу":
            self.vk.send_message("Кто вы?", [from_id], self.start_kb)
        elif event_obj['text'][0] == ';':
            self.vk.send_message(
                f"Сообщение в https://vk.com/gim207896794?sel={event_obj['from_id']}: {event_obj['text'][1:]}",
                [447828812, 284737850, 113688146], self.default_kb)
            self.vk.send_message(f"Сообщение отправлено", [from_id], self.default_kb)
        elif event_obj['text'] == 'Преподаватель':
            self.vk.send_message(f"Введите ФИО", [from_id], self.empty_kb)
        elif event_obj['text'] == 'Студент':
            self.vk.send_message(f"Введите номер группы", [from_id], self.empty_kb)
        elif event_obj['text'] in GROUPS or event_obj['text'] in PROFESSORS:
            if event_obj['text'] in PROFESSORS:
                self.database.set_user_data(
                    from_id,
                    PROFESSORS[event_obj['text']],
                    "professor"
                )
            elif event_obj['text'] in GROUPS:
                self.database.set_user_data(
                    from_id,
                    GROUPS[event_obj['text']],
                    "student"
                )
            self.vk.send_message("Данные сохранены\n", [from_id], self.default_kb)
        elif event_obj['text'] == "Расписание на сегодня":
            resp = self.__get_schedule(from_id, f"{datetime.now().strftime('%d.%m.%Y')}")
            for elem in resp:
                self.vk.send_message(elem, [from_id], self.default_kb)
        elif event_obj['text'] == "Расписание на завтра":
            resp = self.__get_schedule(from_id, f"{(datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')}")
            for elem in resp:
                self.vk.send_message(elem, [from_id], self.default_kb)
        elif event_obj['text'] == "Расписание на другой день":
            self.vk.send_message("Введите дату\n\nПример:\n28.02\n31.10-07.11", [from_id], self.empty_kb)
        elif match(r'\d\d[.]\d\d[-]\d\d[.]\d\d', event_obj['text']):
            start_time = event_obj['text'].split('-')[0] + f".{datetime.now().year}"
            if event_obj['text'].split('-')[0][2:3] > event_obj['text'].split('-')[1][2:3]:
                end_time = event_obj['text'].split('-')[1] + f".{datetime.now().year + 1}"
            else:
                end_time = event_obj['text'].split('-')[1] + f".{datetime.now().year}"
            resp = self.__get_schedule(
                event_obj['from_id'],
                start_time,
                end_time
            )
            for elem in resp:
                self.vk.send_message(elem, [from_id], self.default_kb)
        elif match(r'\d\d[.]\d\d', event_obj['text']):
            resp = self.__get_schedule(
                event_obj['from_id'],
                event_obj['text'] + f".{datetime.now().year}"
            )
            for elem in resp:
                self.vk.send_message(elem, [from_id], self.default_kb)
        else:
            self.vk.send_message("Такой команды нет. Проверьте правильность ввода.", [from_id], self.empty_kb)

    def __get_schedule(self, from_id, start_date, last_date=None):
        db_response = self.database.get_user_data(from_id)
        params = {
            "university_id": db_response["university_id"],
            "id_type": db_response["id_type"],
            "start_date": start_date,
            "last_date": last_date
        }
        return self.schedule.get_schedule_string_array(params)
