import requests


class ChsuApi:
    def __init__(self):
        self.__base_url = "http://api.chsu.ru/api/"
        self.__base_headers = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }

    def __set_new_token(self):
        data = {"password": "ds3m#2nn", "username": "mobil"}
        self.__base_headers["Authorization"] = f'''Bearer {requests.post(
            self.__base_url + "/auth/signin",
            json=data,
            headers=self.__base_headers
        ).json()["data"]}'''

    def get_id_by_professors_list(self):
        self.__set_new_token()
        teachers = self.__get_teachers_list()
        new_list = {}
        for teacher in teachers:
            new_list[teacher["fio"]] = teacher['id']
        return new_list

    def __get_teachers_list(self):
        return requests.get(self.__base_url + "/teacher/v1", headers=self.__base_headers).json()

    def get_professors_by_id_list(self):
        self.__set_new_token()
        teachers = self.__get_teachers_list()
        new_list = {}
        for teacher in teachers:
            new_list[teacher["id"]] = teacher['fio']
        return new_list

    def get_id_by_groups_list(self):
        self.__set_new_token()
        groups = self.__get_groups_list()
        new_list = {}
        for group in groups:
            new_list[group["title"]] = group['id']
        return new_list

    def __get_groups_list(self):
        return requests.get(self.__base_url + "/group/v1", headers=self.__base_headers).json()

    def get_groups_by_id_list(self):
        self.__set_new_token()
        groups = self.__get_groups_list()
        new_list = {}
        for group in groups:
            new_list[group["id"]] = group['title']
        return new_list

    def get_schedule(self, university_id, start_date, last_date=None):
        self.__set_new_token()
        if university_id in self.get_groups_by_id_list():
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/groupId/{university_id}/"
        elif university_id in self.get_professors_by_id_list():
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/lecturerId/{university_id}/"
        else:
            return None
        return requests.get(self.__base_url + query, headers=self.__base_headers).json()
