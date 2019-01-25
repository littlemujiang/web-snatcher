import random
import time

from bs4 import BeautifulSoup
import util.client as client


page_count = 0

def get_config_data_by_id(car_model_id, car_series_data):
    global  page_count
    # browser.get("https://car.autohome.com.cn/config/spec/27911.html")
    query_config_url = f'https://car.autohome.com.cn/config/spec/{car_model_id}.html'
    browser.get(query_config_url)
    # 获取网页html
    config_html_raw = browser.find_element_by_xpath("//*").get_attribute("outerHTML")

    car_config_data = car_series_data.copy()
    config_html = BeautifulSoup(config_html_raw, features="html.parser")
    car_config_table_list = config_html.find_all('table')
    for car_config_table_tag in car_config_table_list:
        # 内容为空校验
        if len(car_config_table_tag) > 0:
            # 过滤出有id的表格
            if car_config_table_tag.attrs.__contains__('id'):
                car_config_table_id = car_config_table_tag.attrs['id']
                car_config_table_id_parts = car_config_table_id.split('_', 1)
                # 过滤出id中包含下划线_的表格
                if len(car_config_table_id_parts) > 1:
                    # 过滤出id为 tab_数字 类型的表格
                    if car_config_table_id_parts[0] == 'tab' and str(car_config_table_id_parts[1]).isdigit():
                        print(car_config_table_id)
                        car_config_item_line_list = car_config_table_tag.find_all('tr')
                        if len(car_config_item_line_list) > 1:
                            # 取配置的分类，如‘基本参数’
                            config_item_title = car_config_item_line_list[0].text
                            config_item_data = {}
                            for car_config_item_index in range(len(car_config_item_line_list)):
                                if car_config_item_index > 0:
                                    car_config_item_line = car_config_item_line_list[car_config_item_index]
                                    car_config_item_title_text, car_config_item_content_text = parse_data_from_tr(browser, car_config_item_line)
                                    if car_config_item_title_text is not None:
                                        config_item_data[car_config_item_title_text] = car_config_item_content_text
                            car_config_data[config_item_title] = config_item_data
    print('====')
    # print(json.dumps(car_config_data))
    if len(list(client.car_config_collection.find({"car_model_id": car_config_data['car_model_id']}))) > 0:
        print(str(car_config_data['car_model_name']) + '已经存在')
    else:
        client.car_config_collection.insert_one(car_config_data)
    # browser.close()
    page_count += 1
    print("***************")
    print(page_count)
    print("***************")
    time.sleep(random.randint(100, 400)/1000)


# 解析一整行的数据
def parse_data_from_tr(browser, car_config_item_line):
    if car_config_item_line is not None and car_config_item_line.attrs.__contains__('id'):
        if len(car_config_item_line.contents) > 1:
            # 取配置的title，如‘厂商/级别’
            car_config_item_title = car_config_item_line.contents[0]
            # 取第一列的数据，如‘AC Schnitzer/中型车’ （后面还有列，不需要）
            car_config_item_content = car_config_item_line.contents[1]
            car_config_item_title_text = translate_content_to_text(browser, car_config_item_title)
            car_config_item_content_text = translate_content_to_text(browser, car_config_item_content)
            # translate_content_to_text(browser, car_config_item_content)
            # print('----')
    return car_config_item_title_text, car_config_item_content_text


def translate_content_to_text(browser, cell_class):
    if cell_class.contents is not None:
        for cell_class_content in cell_class.contents:
            cell_content_list = cell_class_content.contents
            if cell_content_list is not None:
                car_config_item_text = ''
                car_config_item_text = unfold_cell_content(browser, car_config_item_text, cell_content_list)
                return car_config_item_text
                # print('------:' + car_config_item_text)

# 递归展开配置表中的某个单元格
def unfold_cell_content(browser, car_config_item_text, cell_content_list):
    item_text = car_config_item_text
    for cell_content in cell_content_list:
        try:
            if cell_content.attrs.__contains__('class'):
                css_class_name = cell_content.attrs['class'][0]
                item_text = item_text + exec_translate_script(browser, str(css_class_name))
            else:
                item_text = unfold_cell_content(browser, item_text, cell_content.contents)
        except AttributeError:
            item_text = item_text + str(cell_content)
    # print(f'******{item_text}')
    return item_text

# 将classname对应的CSS伪类 进行翻译
def exec_translate_script(browser, css_class_name):
    script = "return window.getComputedStyle(document.getElementsByClassName('" + \
             css_class_name + "')[0], 'before').getPropertyValue('content')"
    translated_text_raw = str(browser.execute_script(script))
    if len(translated_text_raw) > 2:
        translated_text = translated_text_raw[1:-1]
    return translated_text


if __name__ == "__main__":
    # browser = webdriver.Chrome()
    # get_config_data_by_id('27911')
    # client.init_mongodb_conn()

    aaa = {}
    aaa['汉字'] = 'dd'
    bbb = {}
    bbb['基本配置'] = aaa

    # client.car_config_collection.insert_one(bbb)
    print(bbb)