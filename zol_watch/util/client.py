
from pymongo import MongoClient

watch_deal_cnt_collection = None

def init_mongodb_conn():
    global watch_deal_cnt_collection
    mongodb_client = MongoClient('localhost', 27017)
    # processor_db = mongodb_client["car_config_data"]
    zol_db = mongodb_client["zol_data"]
    zol_config_collection = zol_db.watch_config


if __name__ == "__main__":
    init_mongodb_conn()
    processor={}
    processor["app_id"] = "ddddd"


    aaa = {}
    aaa['汉字'] = 'dd'
    bbb = {}
    bbb['基本配置'] = aaa

    watch_deal_cnt_collection.insert_one(bbb)

    processors = list(watch_deal_cnt_collection.find({"app_id": "ddddd"}))

    print('****')

