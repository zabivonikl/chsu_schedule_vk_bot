from pymongo import MongoClient

from tokens import MONGO_DB_LOGIN, MONGO_DB_PASSWORD, MONGO_DB_NAME


class MongoDB:
    def __init__(self):
        self.__client = MongoClient(
            f"mongodb+srv://{MONGO_DB_LOGIN}:{MONGO_DB_PASSWORD}"
            f"@cluster.rfoam.mongodb.net/"
            f"{MONGO_DB_NAME}?"
            f"retryWrites=true&"
            f"w=majority",
            port=27017,
        )
        self.__users_collection = self.__client[MONGO_DB_NAME]["Users"]

    def get_user_data(self, platform_id, api_name):
        bot_user = self.__users_collection.find_one({"id": platform_id, "platform": api_name})
        if bot_user is not None:
            return {
                "group_name": bot_user["group_name"],
                "professor_name": bot_user["professor_name"]
            }
        else:
            return None

    def set_user_data(self, user_id, university_id, api_name,
                      group_name=None, mailing_time=None, professor_name=None):
        self.__users_collection.find_one_and_delete({"id": user_id, "platform": api_name})
        self.__users_collection.insert_one({
            "id": user_id,
            "university_id": university_id,
            "platform": api_name,
            "mailing_time": mailing_time,
            "group_name": group_name,
            "professor_name": professor_name
        })

    def update_mailing_time(self, user_id, api_name, time=None):
        self.__users_collection.update_one({
            "id": user_id,
            "platform": api_name,
        }, {
            "$set": {
                "mailing_time": time
            }
        })

    def get_mailing_subscribers_by_time(self, time):
        subscribers = self.__users_collection.find({"mailing_time": time})
        simplified_subscribers = []
        for subscriber in subscribers:
            simplified_subscribers.append([subscriber["id"], subscriber["platform"]])
        return simplified_subscribers
