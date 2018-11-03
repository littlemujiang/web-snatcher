
from selenium import webdriver
from bs4 import BeautifulSoup

if __name__ == "__main__":
    browser = webdriver.Chrome()
    # browser = webdriver.Firefox()

    browser.get("https://car.autohome.com.cn/config/spec/27911.html")

    html = browser.find_element_by_xpath("//*").get_attribute("outerHTML")

    car_config_table_list_html = BeautifulSoup(html)
    car_config_table_list = car_config_table_list_html.find_all('table')
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
                        for car_config_item_line in car_config_item_line_list:
                            if car_config_item_line is not None and car_config_item_line.attrs.__contains__('id') and car_config_item_line.attrs['id'] == 'tr_16':
                                class_name = car_config_item_line.contents[1].contents[0].contents[1].attrs['class']
                                script = "return window.getComputedStyle(document.getElementsByClassName('" + class_name[0] + "')[0], 'before').getPropertyValue('content')"
                                pseudo_element_content = browser.execute_script(script)
                                print('------')
                            else:
                                continue

    # config_info = browser.find_element_by_id('tab_0')

    # print(browser.find_element_by_id('config_data'))
    browser.close()