from datetime import datetime, timedelta
from re import match

from APIs.ChsuAPI.chsu import ChsuApi
from DataHandlers.schedule_parser import ScheduleParser


class EventHandler:
    def __init__(self, api, database):
        self.__chat_platform = api
        self.__database = database
        self.__schedule = ScheduleParser()
        self.__chsu_api = ChsuApi()

        self.__standard_kb = self.__chat_platform.get_standard_keyboard()
        self.__start_kb = self.__chat_platform.get_start_keyboard()
        self.__empty_kb = self.__chat_platform.get_empty_keyboard()
        self.__canceling_kb = self.__chat_platform.get_canceling_keyboard()

        self.__professors = self.__chsu_api.get_professors_list()
        self.__groups = self.__chsu_api.get_groups_list()

    def handle_event(self, event_obj):
        from_id = event_obj['from_id']
        text = event_obj['text']

        if text == 'Начать' or text == "/start" or text == "Изменить группу":
            self.__chat_platform.send_message("Кто вы?", [from_id], self.__start_kb)
        elif text[0] == ';':
            self.__send_message_to_admins(text[1:], from_id)
        elif text == 'Преподаватель':
            self.__chat_platform.send_message(f"Введите ФИО", [from_id], self.__empty_kb)
        elif text == 'Студент':
            self.__chat_platform.send_message(f"Введите номер группы", [from_id], self.__empty_kb)
        elif text in self.__groups or text in self.__professors:
            self.__set_university_id(text, from_id)
        elif text == "Расписание на сегодня":
            resp = self.__get_schedule(from_id, f"{datetime.now().strftime('%d.%m.%Y')}")
            self.__chat_platform.send_message_queue(resp, [from_id], self.__standard_kb)
        elif text == "Расписание на завтра":
            resp = self.__get_schedule(from_id, f"{(datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')}")
            self.__chat_platform.send_message_queue(resp, [from_id], self.__standard_kb)
        elif text == "Расписание на другой день":
            self.__chat_platform.send_message(
                "Введите дату\n"
                "\n"
                "Пример: 08.02 - запрос расписания для конкретного дня\n"
                "31.10-07.11 - запрос расписания для заданного интервала дат",
                [from_id],
                self.__canceling_kb
            )
        elif text == "Отмена":
            self.__chat_platform.send_message(f"Действие отменено", [from_id], self.__standard_kb)
        elif match(r'[0-3]\d[.][0-1]\d[-][0-3]\d[.][0-1]\d', text):
            self.__handle_custom_date(from_id, text.split('-')[0], text.split('-')[1])
        elif match(r'[0-3]\d[.][0-1]\d', text):
            self.__handle_custom_date(from_id, text)
        elif text == "Рассылка":
            self.__send_mailing_info(from_id)
        elif text == "Отписаться":
            self.__delete_mailing_time(from_id)
        elif match(r'[0-2]\d[:][0-5]\d', text):
            self.__set_mailing_time(from_id, text)
        else:
            self.__chat_platform.send_message("Такой команды нет. Проверьте правильность ввода.", [from_id],
                                              self.__standard_kb)

    def __send_message_to_admins(self, message, from_id):
        self.__chat_platform.send_message(
            f"Сообщение в https://vk.com/gim207896794?sel={from_id}: {message}",
            self.__chat_platform.get_admins(), self.__standard_kb)
        self.__chat_platform.send_message(f"Сообщение отправлено", [from_id], self.__standard_kb)

    def __set_university_id(self, university_id, from_id):
        if university_id in self.__professors:
            self.__database.set_user_data(
                from_id,
                self.__professors[university_id],
                "professor",
                self.__chat_platform.get_api_name(),
                group_name=university_id
            )
        elif university_id in self.__groups:
            self.__database.set_user_data(
                from_id,
                self.__groups[university_id],
                "student",
                self.__chat_platform.get_api_name(),
                group_name=university_id
            )
        self.__chat_platform.send_message("Данные сохранены\n", [from_id], self.__standard_kb)

    def __handle_custom_date(self, from_id, start_date, end_date=None):
        dates = self.__get_full_date(start_date, end_date)
        resp = self.__get_schedule(from_id, dates[0], dates[1])
        self.__chat_platform.send_message_queue(resp, [from_id], self.__standard_kb)

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
        db_response = self.__database.get_user_data(from_id, self.__chat_platform.get_api_name())
        try:
            response = self.__chsu_api.get_schedule(
                university_id=int(db_response["university_id"]),
                id_type=db_response["id_type"],
                start_date=start_date,
                last_date=last_date
            )
            if response:
                response = self.__schedule.parse_json(db_response["id_type"], response)
                return response
            else:
                return self.__schedule.get_empty_response()
        except Exception as err:
            print(err)
            return ['Что-то пошло не так. Вероятно, не работает сайт ЧГУ.']

    def __delete_mailing_time(self, from_id):
        self.__database.update_mailing_time(from_id, self.__chat_platform.get_api_name())
        self.__chat_platform.send_message(
            f"Вы отписались от рассылки.",
            [from_id],
            self.__standard_kb
        )

    def __set_mailing_time(self, from_id, text):
        self.__database.update_mailing_time(from_id, self.__chat_platform.get_api_name(), text)
        self.__chat_platform.send_message(
            f"Вы подписались на рассылку расписания."
            f" Теперь, ежедневно в {text}, Вы будете получать расписание на следующий день.",
            [from_id],
            self.__standard_kb
        )

    def __send_mailing_info(self, from_id):
        self.__chat_platform.send_message(
            "Введите время рассылки\n"
            "Пример: 08:36\n"
            "\n"
            "Для отписки напишите \"Отписаться\" (соблюдая регистр).",
            [from_id], self.__canceling_kb)
