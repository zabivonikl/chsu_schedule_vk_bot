from datetime import datetime, timedelta
from re import match

from vk_api.keyboard import VkKeyboard

from id_lists import GROUPS, PROFESSORS
from site_schedule import SiteSchedule


class EventHandler:
    def __init__(self, vk, database):
        self.__vk = vk
        self.__database = database
        self.__schedule = SiteSchedule()

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
        self.__default_kb = default_kb.get_keyboard()

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
        self.__start_kb = start_kb.get_keyboard()

    def __get_empty_keyboard(self):
        self.__empty_kb = VkKeyboard.get_empty_keyboard()

    def handle_event(self, event_obj):
        from_id = event_obj['from_id']
        text = event_obj['text']

        if text == 'Начать' or text == "Изменить группу":
            self.__send_start_message(from_id)
        elif text[0] == ';':
            self.__send_message_to_admins(text[1:], from_id)
        elif text == 'Преподаватель':
            self.__vk.send_message(f"Введите ФИО", [from_id], self.__empty_kb)
        elif text == 'Студент':
            self.__vk.send_message(f"Введите номер группы", [from_id], self.__empty_kb)
        elif text in GROUPS or text in PROFESSORS:
            self.__set_university_id(text, from_id)
        elif text == "Расписание на сегодня":
            resp = self.__get_schedule(from_id, f"{datetime.now().strftime('%d.%m.%Y')}")
            self.__vk.send_message_queue(resp, [from_id], self.__default_kb)
        elif text == "Расписание на завтра":
            resp = self.__get_schedule(from_id, f"{(datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')}")
            self.__vk.send_message_queue(resp, [from_id], self.__default_kb)
        elif text == "Расписание на другой день":
            self.__vk.send_message("Введите дату\n\nПример:\n28.02\n31.10-07.11", [from_id], self.__empty_kb)
        elif match(r'\d\d[.]\d\d[-]\d\d[.]\d\d', text):
            self.__handle_custom_date(from_id, text.split('-')[0], text.split('-')[1])
        elif match(r'\d\d[.]\d\d', text):
            self.__handle_custom_date(from_id, text)
        else:
            self.__vk.send_message("Такой команды нет. Проверьте правильность ввода.", [from_id], self.__empty_kb)

    def __send_start_message(self, from_id):
        self.__vk.send_message("Кто вы?", [from_id], self.__start_kb)

    def __send_message_to_admins(self, message, from_id):
        self.__vk.send_message(
            f"Сообщение в https://vk.com/gim207896794?sel={from_id}: {message}",
            [447828812, 284737850, 113688146], self.__default_kb)
        self.__vk.send_message(f"Сообщение отправлено", [from_id], self.__default_kb)

    def __set_university_id(self, university_id, from_id):
        if university_id in PROFESSORS:
            self.__database.set_user_data(from_id, PROFESSORS[university_id], "professor")
        elif university_id in GROUPS:
            self.__database.set_user_data(from_id, GROUPS[university_id], "student")
        self.__vk.send_message("Данные сохранены\n", [from_id], self.__default_kb)

    def __handle_custom_date(self, from_id, start_date, end_date=None):
        dates = self.__get_full_date(start_date, end_date)
        resp = self.__get_schedule(from_id, dates[0], dates[1])
        self.__vk.send_message_queue(resp, [from_id], self.__default_kb)

    @staticmethod
    def __get_full_date(start_date_string, end_date_string=None):
        start_date = start_date_string.split('-')[0] + f".{datetime.now().year}"
        end_date = None

        if end_date_string:
            if end_date_string[2:3] < start_date_string[2:3]:
                end_date = end_date_string + f".{datetime.now().year + 1}"
            else:
                end_date = end_date_string + f".{datetime.now().year}"

        return [start_date, end_date]

    def __get_schedule(self, from_id, start_date, last_date=None):
        db_response = self.__database.get_user_data(from_id)
        params = {
            "university_id": db_response["university_id"],
            "id_type": db_response["id_type"],
            "start_date": start_date,
            "last_date": last_date
        }
        return self.__schedule.get_schedule_string_array(params)
