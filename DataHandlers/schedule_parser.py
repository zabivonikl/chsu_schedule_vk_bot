class ScheduleParser:
    def __init__(self):
        self.__nullify_fields()
        self.__response_json = None

    def __nullify_fields(self):
        self.__response = []
        self.__lesson = {}
        self.__current_date = ""

    def parse_json(self, id_type, json):
        self.__response_json = json
        self.__nullify_fields()
        for self.__lesson in self.__response_json:
            self.__split_if_another_day()
            self.__add_lesson_to_string(id_type)
        return self.__response

    def __split_if_another_day(self):
        if not self.__is_current_date():
            self.__update_current_and_add_day()

    def __is_current_date(self):
        return self.__current_date == self.__lesson['dateEvent']

    def __update_current_and_add_day(self):
        self.__current_date = self.__lesson['dateEvent']
        self.__response.append(f'\n=====Расписание на {self.__current_date}=====\n')

    def __add_lesson_to_string(self, id_type):
        self.__response[len(self.__response) - 1] += self.__get_lesson_time()
        self.__response[len(self.__response) - 1] += self.__get_discipline_string()
        self.__response[len(self.__response) - 1] += self.__get_professors_names() if id_type == 'student' \
            else self.__get_groups_names()
        self.__response[len(self.__response) - 1] += self.__get_location()
        self.__response[len(self.__response) - 1] += "\n"

    def __get_lesson_time(self):
        return f"{self.__lesson['startTime']}-{self.__lesson['endTime']}\n"

    def __get_discipline_string(self):
        return f"{self.__lesson['abbrlessontype'] or ''}., {self.__lesson['discipline']['title']}\n"

    def __get_professors_names(self):
        response = ""
        for professor in self.__lesson['lecturers']:
            response += f"{professor['fio']}, "
        return response[:-2] + "\n"

    def __get_groups_names(self):
        response = ""
        for group in self.__lesson['groups']:
            response += f"{group['title']}, "
        return response[:-2] + "\n"

    def __get_location(self):
        return "Онлайн\n" if self.__lesson['online'] == 1 else self.__get_address()

    def __get_address(self):
        return f"{self.__lesson['build']['title']}, аудитория {self.__lesson['auditory']['title']}\n"

    @staticmethod
    def get_empty_response():
        return ["На текущий промежуток времени расписание не найдено\n"]
