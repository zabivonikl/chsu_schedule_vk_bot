from json import loads

from requests import get


class SiteSchedule:
    def __init__(self):
        self.url = 'https://www.chsu.ru/raspisanie' \
                   '?p_p_id=TimeTable_WAR_TimeTableportlet' \
                   '&p_p_lifecycle=2&p_p_state=normal' \
                   '&p_p_mode=view' \
                   '&p_p_cacheability=cacheLevelPage' \
                   '&p_p_col_id=column-1' \
                   '&p_p_col_count=1'
        self.params = {
            "_TimeTable_WAR_TimeTableportlet_cmd": "timeTable",
            "_TimeTable_WAR_TimeTableportlet_typeTimeTable": "period"
        }

    def get_schedule_string_array(self, request_parameters):
        self.__set_request_params(request_parameters)
        self.__get_response_json()
        return self.__parse_json(request_parameters["id_type"]) or self.__get_empty_response()

    def __set_request_params(self, request_parameters):
        self.params = {
            **self.params,
            "_TimeTable_WAR_TimeTableportlet_group": request_parameters["university_id"],
            "_TimeTable_WAR_TimeTableportlet_type": request_parameters["id_type"],
            "_TimeTable_WAR_TimeTableportlet_startDate": request_parameters["start_date"],
            "_TimeTable_WAR_TimeTableportlet_endDate": request_parameters["last_date"] or request_parameters[
                "start_date"],
            "_TimeTable_WAR_TimeTableportlet_professor": request_parameters["university_id"]
        }

    def __get_response_json(self):
        resp = get(self.url, params=self.params)
        self.response_json = loads(resp.text)

    # TODO сделать человеческую итерацию по дням
    def __parse_json(self, id_type):
        resp = []
        current_date = ""
        iterator = -1
        self.lesson = {}
        for self.lesson in self.response_json:
            if current_date != self.lesson['dateEvent']:
                current_date = self.lesson['dateEvent']
                iterator += 1
                resp.append(f'\n=====Расписание на {current_date}=====\n')
            resp[iterator] += self.__get_lesson_time()
            resp[iterator] += self.__get_discipline_string()
            resp[iterator] += self.__get_professors_names() if id_type == 'student' else self.__get_groups_names()
            resp[iterator] += self.__get_location()
            resp[iterator] += "\n"
        return resp

    def __get_lesson_time(self):
        return f"{self.lesson['startTime']}-{self.lesson['endTime']}\n"

    def __get_discipline_string(self):
        return f"{self.lesson['abbrlessontype'] or ''}., {self.lesson['discipline']['title']}\n"

    def __get_professors_names(self):
        response = ""
        for professor in self.lesson['lecturers']:
            response += f"{professor['fio']}, "
        return response[:-2] + "\n"

    def __get_groups_names(self):
        response = ""
        for group in self.lesson['groups']:
            response += f"{group['title']}, "
        return response[:-2] + "\n"

    def __get_location(self):
        return "Онлайн\n" if self.lesson['online'] == 1 else self.__get_address()

    def __get_address(self):
        return f"{self.lesson['build']['title']}, аудитория {self.lesson['auditory']['title']}\n"

    @staticmethod
    def __get_empty_response():
        return ["На текущий промежуток времени расписание не найдено\n"]
