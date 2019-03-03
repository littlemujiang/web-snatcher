# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import json
from datetime import time
from time import sleep

import scrapy
import zol_watch.util.client as client
from bs4 import BeautifulSoup
from selenium import webdriver


def parse():
    browser = webdriver.Chrome()
    data_url = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest'
    browser.get(data_url)
    # 获取网页html
    config_html_raw = browser.find_element_by_xpath("//*").get_attribute("outerHTML")

def getCookie():
    # driver = webdriver.PhantomJS(executable_path='/Users/mujiang/Documents/program files/phantomjs-2.1.1-macosx/bin/phantomjs')

    driver = webdriver.Chrome()

    # driver.get('https://login.taobao.com/member/login.jhtml')
    #
    # driver.find_element_by_id("J_Quick2Static").click()
    # driver.find_element_by_id("TPL_username_1").clear()
    # driver.find_element_by_id("TPL_password_1").clear()
    # driver.find_element_by_id("TPL_username_1").send_keys('13681263532')
    # sleep(2)
    # driver.find_element_by_id("TPL_password_1").send_keys('xlchen6b40810@')
    # sleep(3)
    # driver.find_element_by_id("J_SubmitStatic").click()
    #
    # # driver.get_cookies()取得cookie
    # # cookie = "; ".join([item["name"] + "=" + item["value"] + "\n" for item in driver.get_cookies()])
    # cookie = driver.get_cookies()
    # print(cookie)

    data_url = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest'
    driver.get(data_url)
    # driver.find_element_by_id("J_Quick2Static").click()
    # driver.find_element_by_id("TPL_username_1").clear()
    # driver.find_element_by_id("TPL_password_1").clear()
    # driver.find_element_by_id("TPL_username_1").send_keys('13681263532')
    # sleep(2)
    # driver.find_element_by_id("TPL_password_1").send_keys('xlchen6b40810@')
    # sleep(3)
    # driver.find_element_by_id("J_SubmitStatic").click()
    cookie = driver.get_cookies()
    driver.add_cookie(cookie[4])

    data_url2 = 'https://s.taobao.com/search?q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190303&ie=utf8&cps=yes&ppath=20000%3A11813&sort=sale-desc&bcoffset=0&p4ppushleft=%2C44&s=128'
    driver.get(data_url2)
    config_html_raw = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
    config_html = BeautifulSoup(config_html_raw, features="html.parser")
    car_config_table_list = config_html.find_all('table')

    car_config_table_list = config_html.find_all('table')
    for car_config_table_tag in car_config_table_list:
        # 内容为空校验
        if len(car_config_table_tag) > 0:
            # 过滤出有id的表格
            if car_config_table_tag.attrs.__contains__('id'):
                car_config_table_id = car_config_table_tag.attrs['id']
                car_config_table_id_parts = car_config_table_id.split('_', 1)

if __name__ == "__main__":
    # parse()
    # getCookie()

    price = None

    aaa = price.strip() if price else None

    print(aaa)