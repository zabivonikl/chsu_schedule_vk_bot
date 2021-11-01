import requests


class ChsuApi:
    def __init__(self):
        self.__base_url = "http://api.chsu.ru/api/"
        self.__base_headers = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }

    def get_professors_list(self):
        self.__set_new_token()
        teachers = requests.get(self.__base_url + "/teacher/v1", headers=self.__base_headers)
        return self.__simplify_teachers_list(teachers.json())

    def __set_new_token(self):
        data = {"password": "ds3m#2nn", "username": "mobil"}
        self.__base_headers["Authorization"] = requests.post(
            self.__base_url + "/auth/signin",
            json=data,
            headers=self.__base_headers
        ).json()["data"]

    @staticmethod
    def __simplify_teachers_list(teachers_list):
        new_list = {}
        for teacher in teachers_list:
            new_list[teacher["fio"]] = teacher['id']
        return new_list

    def get_groups_list(self):
        self.__set_new_token()
        groups = requests.get(self.__base_url + "/group/v1", headers=self.__base_headers)
        return self.__simplify_groups_list(groups.json())

    @staticmethod
    def __simplify_groups_list(groups_list):
        new_list = {}
        for group in groups_list:
            new_list[group["title"]] = group['id']
        return new_list

    def get_schedule(self, university_id, id_type, start_date, last_date=None):
        self.__set_new_token()
        if id_type == "student":
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/groupId/{university_id}/"
        else:
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/lecturerId/{university_id}/"
        return requests.get(self.__base_url + query, headers=self.__base_headers).json()


if __name__ == "__main__":
    print(ChsuApi().get_groups_list())
