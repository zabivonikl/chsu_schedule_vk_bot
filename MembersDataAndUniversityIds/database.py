from sqlite3 import connect


class Database:
    def __init__(self):
        self.__path = 'MembersDataAndUniversityIds/users.db'

    def get_user_data(self, platform_id, api_name):
        with connect(self.__path) as conn:
            curs = conn.cursor()
            curs.execute(f"SELECT * FROM ids WHERE (id, platform)=('{platform_id}', '{api_name}')")
            response = curs.fetchone()
        return {
            "university_id": response[1],
            "id_type": response[2]
        }

    def set_user_data(self, vk_id, university_id, role, api_name):
        with connect(self.__path) as conn:
            curs = conn.cursor()
            curs.execute(
                f'''INSERT OR REPLACE INTO ids (id, chsu_id, id_type, platform) VALUES ({vk_id}, {university_id}, "{role}", "{api_name}")'''
            )
