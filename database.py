from sqlite3 import connect


class Database:
    def __init__(self):
        self.path = 'users.db'

    def get_user_data(self, vk_id):
        with connect(self.path) as conn:
            curs = conn.cursor()
            curs.execute(f"SELECT * FROM ids WHERE vk_id='{vk_id}'")
            response = curs.fetchone()
        return {
            "university_id": response[1],
            "id_type": response[2]
        }

    def set_user_data(self, vk_id, university_id, role):
        with connect(self.path) as conn:
            curs = conn.cursor()
            curs.execute(
                f'''INSERT OR REPLACE INTO ids (vk_id, chsu_id, id_type) VALUES ({vk_id}, {university_id}, "{role}")'''
            )
