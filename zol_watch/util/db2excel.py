import xlwt
from pymongo import MongoClient
from xlwt import Pattern

global config_inner_items
global config_multimedia_items
global config_glass_items
global sheet_map
global sheet_col_index_map

def write_doc_2_excel():
    global sheet_map
    global sheet_col_index_map
    car_config_data_collection = init_mongodb_conn()
    config_list = list(car_config_data_collection.find({}))

    data_csv = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = data_csv.add_sheet("watch_config", cell_overwrite_ok=True)
    sheet.write(0, 0, "品牌名")
    sheet.write(0, 1, "手表名")
    sheet.write(0, 2, "适用人群")
    sheet.write(0, 3, "屏幕尺寸")
    sheet.write(0, 4, "存储容量")
    sheet.write(0, 5, "系统内存")
    sheet.write(0, 6, "操作系统")
    sheet.write(0, 7, "处理器")
    sheet.write(0, 8, "屏幕分辨率")
    sheet.write(0, 9, "屏幕材质")
    item_count = len(config_list)
    for index in range(item_count):
        detail = config_list[index]
        raw_index = index + 1
        sheet.write(raw_index, 0, detail["watch_brand_name"])
        sheet.write(raw_index, 1, detail["watch_name"])
        if detail.__contains__("main_config") and len(detail["main_config"]) > 0:
            config = detail["main_config"]
            sheet.write(raw_index, 2, config.get("适用人群"))
            sheet.write(raw_index, 3, config.get("屏幕尺寸"))
            sheet.write(raw_index, 4, config.get("存储容量"))
            sheet.write(raw_index, 5, config.get("系统内存"))
            sheet.write(raw_index, 6, config.get("操作系统"))
            sheet.write(raw_index, 7, config.get("处理器"))
            sheet.write(raw_index, 8, config.get("屏幕分辨率"))
            sheet.write(raw_index, 9, config.get("屏幕材质"))
    data_csv.save(rf'D:\zol\watch_data.xls')


def init_mongodb_conn():
    global car_config_collection
    mongodb_client = MongoClient('localhost', 27017)
    # processor_db = mongodb_client["car_config_data"]
    zol_db = mongodb_client["zol_data"]
    car_config_collection = zol_db.watch_config
    return car_config_collection


if __name__ == "__main__":
    write_doc_2_excel()
