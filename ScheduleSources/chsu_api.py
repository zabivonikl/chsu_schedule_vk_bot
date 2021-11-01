import requests


class ChsuApi:
    def __init__(self):
        self.__base_url = "http://api.chsu.ru/api/"

    def get_professors_list(self):
        headers = {
            "Content-Type": "application/json",
            "charset": "utf-8",
            "Authorization": f"Bearer {self.__get_new_token()}"
        }
        teachers = requests.get(self.__base_url + "/teacher/v1", headers=headers)
        return self.__simplify_teachers_list(teachers.json())

    def __get_new_token(self):
        headers = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }
        data = {"password": "ds3m#2nn", "username": "mobil"}
        return requests.post(self.__base_url + "/auth/signin", json=data, headers=headers).json()["data"]

    @staticmethod
    def __simplify_teachers_list(teachers_list):
        new_list = {}
        for teacher in teachers_list:
            new_list[teacher["fio"]] = teacher['id']
        return new_list

    def get_groups_list(self):
        headers = {
            "Content-Type": "application/json",
            "charset": "utf-8",
            "Authorization": f"Bearer {self.__get_new_token()}"
        }
        groups = requests.get(self.__base_url + "/group/v1", headers=headers)
        return self.__simplify_groups_list(groups.json())

    @staticmethod
    def __simplify_groups_list(groups_list):
        new_list = {}
        for group in groups_list:
            new_list[group["title"]] = group['id']
        return new_list

    def get_schedule(self, university_id, id_type, start_date, last_date=None):
        headers = {
            "Content-Type": "application/json",
            "charset": "utf-8",
            "Authorization": f"Bearer {self.__get_new_token()}"
        }
        if id_type == "student":
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/groupId/{university_id}/"
            return requests.get(self.__base_url + query, headers=headers).json()
        else:
            query = f"/timetable/v1/from/{start_date}/to/{last_date or start_date}/lecturerId/{university_id}/"
            return requests.get(self.__base_url + query, headers=headers).json()


if __name__ == "__main__":
    print(ChsuApi().get_groups_list())
