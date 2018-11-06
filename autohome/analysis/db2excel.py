import xlwt
from pymongo import MongoClient

global config_inner_items
global config_multimedia_items
global config_glass_items
global sheet_map
global sheet_col_index_map

def write_doc_2_excel(alphabet):
    global sheet_map
    global sheet_col_index_map
    car_config_data_collection = init_mongodb_conn()
    config_list = list(car_config_data_collection.find({"car_brand_index": alphabet}))

    config_dict = list(car_config_data_collection.find({"_id": "autohome_config_dict"}))
    data_csv = xlwt.Workbook(encoding='utf-8', style_compression=0)

    init_sheet_catalog_map(config_dict[0])
    # sheet表单的字典，存放某一品牌的车
    sheet_map = {}
    # sheet表单的当前列的字典，存放某一品牌的车的处理位置
    sheet_col_index_map = {}
    for config in config_list:
        if not config.__contains__('car_brand_name'):
            continue
        if sheet_map.get(config['car_brand_name']) is None:
            sheet_brand = data_csv.add_sheet(config['car_brand_name'], cell_overwrite_ok=True)
            init_sheet_catalog(sheet_brand)
            sheet_map[config['car_brand_name']] = sheet_brand
            col_index = 3
            sheet_col_index_map[config['car_brand_name']] = col_index
        else:
            sheet_brand = sheet_map.get(config['car_brand_name'])
            col_index = sheet_col_index_map.get(config['car_brand_name'])

        write_data_2_sheet(sheet_brand, col_index, config)
        data_csv.save(r'./A_car.xls')


def write_data_2_sheet(sheet, col_index, config_data):
    global config_inner_items
    global config_multimedia_items
    global config_glass_items
    global sheet_col_index_map

    row_index = 2
    sheet.write(0, col_index, config_data['car_series_name'])
    sheet.write(1, col_index, config_data['car_model_name'])

    if config_data.__contains__('内部配置'):
        config_inner = config_data['内部配置']
        # config_inner_items = list(config_inner.keys())
        for index in range(len(config_inner_items)):
            if config_inner.__contains__(config_inner_items[index]):
                sheet.write(row_index + index, col_index, config_inner[config_inner_items[index]])
    row_index = row_index + len(config_inner_items)

    if config_data.__contains__('多媒体配置'):
        config_multimedia = config_data['多媒体配置']
        # config_multimedia_items = list(config_multimedia.keys())
        for index in range(len(config_multimedia_items)):
            if config_multimedia.__contains__(config_multimedia_items[index]):
                sheet.write(row_index + index, col_index, config_multimedia[config_multimedia_items[index]])
    row_index = row_index + len(config_multimedia_items)

    if config_data.__contains__('玻璃/后视镜'):
        config_glass = config_data['玻璃/后视镜']
        # config_glass_items = list(config_glass.keys())
        for index in range(len(config_glass_items)):
            if config_glass.__contains__(config_glass_items[index]):
                sheet.write(row_index + index, col_index, config_glass[config_glass_items[index]])

    row_index = row_index + len(config_glass_items)
    col_index += 1
    sheet_col_index_map[config_data['car_brand_name']] = col_index
    # print('***')


def init_sheet_catalog(sheet):
    global config_inner_items
    global config_multimedia_items
    global config_glass_items

    style = xlwt.XFStyle()  # 创建一个样式对象，初始化样式
    al = xlwt.Alignment()
    al.horz = 0x02  # 设置水平居中
    al.vert = 0x01  # 设置垂直居中
    style.alignment = al

    font = xlwt.Font()  # 为样式创建字体
    font.name = 'Times New Roman'
    font.bold = True  # 黑体
    # font.underline = True  # 下划线
    # font.italic = True  # 斜体字
    style.font = font  # 设定样式

    row_index = 2
    # config_inner = config_data['内部配置']
    # config_inner_items = list(config_inner.keys())
    sheet.write_merge(row_index,  row_index + len(config_inner_items) -1 , 0, 0+0, "内部配置", style)
    for index in range(len(config_inner_items)):
        sheet.write(row_index + index , 1, config_inner_items[index])
    row_index = row_index + len(config_inner_items)

    # config_multimedia = config_data['多媒体配置']
    # config_multimedia_items = list(config_multimedia.keys())
    sheet.write_merge(row_index, row_index + len(config_multimedia_items)-1 , 0, 0+0, "多媒体配置", style)
    for index in range(len(config_multimedia_items)):
        sheet.write(row_index + index , 1, config_multimedia_items[index])
    row_index = row_index + len(config_multimedia_items)

    # config_glass = config_data['玻璃/后视镜']
    # config_glass_items = list(config_glass.keys())
    sheet.write_merge(row_index ,row_index + len(config_glass_items)-1, 0, 0+0, "玻璃/后视镜", style)
    for index in range(len(config_glass_items)):
        sheet.write(row_index + index , 1, config_glass_items[index])
    row_index = row_index + len(config_glass_items)

def init_sheet_catalog_map(config_data):
    global config_inner_items
    global config_multimedia_items
    global config_glass_items

    config_inner = config_data['内部配置']
    config_inner_items = list(config_inner.keys())

    config_multimedia = config_data['多媒体配置']
    config_multimedia_items = list(config_multimedia.keys())

    config_glass = config_data['玻璃/后视镜']
    config_glass_items = list(config_glass.keys())



def init_sheet_catalog_dict():
    car_config_data_collection = init_mongodb_conn()
    config_list = list(car_config_data_collection.find({}))

    config_data_dict = {}
    for config in config_list:
        for config_key in config.keys():
            if config_key not in config_data_dict.keys():
               config_data_dict[config_key] = {}
            config_key_map = config_data_dict[config_key]
            config_item_map = config[config_key]
            if not isinstance(config_item_map, dict):
                continue
            for config_itme_key in config_item_map.keys():
                if config_itme_key not in config_key_map.keys():
                    config_key_map[config_itme_key] = {}
                config_key_map[config_itme_key] = 1
    config_data_dict['_id'] = 'autohome_config_dict'
    car_config_data_collection.insert_one(config_data_dict)
    print(config_data_dict)


def init_mongodb_conn():
    global car_config_collection
    mongodb_client = MongoClient('localhost', 27017)
    # processor_db = mongodb_client["car_config_data"]
    processor_db = mongodb_client["autohome_data"]
    car_config_collection = processor_db.car_config
    return car_config_collection


if __name__ == "__main__":
    write_doc_2_excel('A')
    # init_sheet_catalog_dict()