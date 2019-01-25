
from pymongo import MongoClient

car_config_collection = None

def init_mongodb_conn():
    global car_config_collection
    mongodb_client = MongoClient('localhost', 27017)
    # processor_db = mongodb_client["car_config_data"]
    processor_db = mongodb_client["autohome_data"]
    car_config_collection = processor_db.car_config

if __name__ == "__main__":
    init_mongodb_conn()
    processor={}
    processor["app_id"] = "ddddd"


    aaa = {}
    aaa['汉字'] = 'dd'
    bbb = {}
    bbb['基本配置'] = aaa

    car_config_collection.insert_one(bbb)

    processors = list(car_config_collection.find({"app_id": "ddddd"}))

    print('****')

