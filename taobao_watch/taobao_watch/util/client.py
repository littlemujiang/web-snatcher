
from pymongo import MongoClient



watch_deal_cnt_collection = None

def init_mongodb_conn():
    global watch_deal_cnt_collection
    mongodb_client = MongoClient('localhost', 27017)
    # processor_db = mongodb_client["car_config_data"]
    taobao_db = mongodb_client["taobao_data"]
    watch_deal_cnt_collection = taobao_db.watch_deal_cnt


if __name__ == "__main__":
    init_mongodb_conn()
    processor={}
    processor["item_id"] = "ddddd"

    # taobao_watch_deal_cnt_collection.insert_one(processor)

    processors = list(watch_deal_cnt_collection.find({"item_id": "ddddd"}))

    print('****')

