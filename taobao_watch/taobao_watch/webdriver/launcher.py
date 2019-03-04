
import json
import random
from datetime import time
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

import taobao_watch.taobao_watch.util.client as client

browser = None

def init():
    client.init_mongodb_conn()
    initBrowser()
    initCookie()

def initBrowser():
    global browser

    # chrome_profile = webdriver.ChromeOptions()
    # chrome_profile.add_argument('--proxy-server=http://10.0.0.12:8080')
    #
    # # browser = webdriver.Chrome()
    # browser = webdriver.Chrome(options=chrome_profile)

    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', 'localhost')
    profile.set_preference('network.proxy.http_port', 8080)  # int
    profile.update_preferences()

    browser = webdriver.Firefox(firefox_profile=profile)


def initCookie():

    data_url = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest'
    browser.get(data_url)
    # driver.find_element_by_id("J_Quick2Static").click()
    # driver.find_element_by_id("TPL_username_1").clear()
    # driver.find_element_by_id("TPL_password_1").clear()
    # driver.find_element_by_id("TPL_username_1").send_keys('13681263532')
    # sleep(2)
    # driver.find_element_by_id("TPL_password_1").send_keys('xlchen6b40810@')
    # sleep(3)
    # driver.find_element_by_id("J_SubmitStatic").click()
    cookie = browser.get_cookies()
    browser.add_cookie(cookie[4])


def parseModel():
    model_list_page = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest'
    browser.get(model_list_page)
    model_list_html_raw = browser.find_element_by_id('J_NavCommonRowItems_0').get_attribute("outerHTML")

    model_list_html = BeautifulSoup(model_list_html_raw, features="html.parser")
    model_list_tag = model_list_html.findAll(name='a', attrs={"class": "item icon-tag J_Ajax "})

    model_path_dict = {}

    for model_tag in model_list_tag:
        # 内容为空校验
        if len(model_tag) > 0:
            model_name = model_tag['title']
            if model_name in ['WeLoop']:
                continue
            model_path = model_tag['trace-click']
            model_paths = model_path.split(';')
            if len(model_paths) != 2:
                continue
            ppath = model_paths[1]
            ppaths = ppath.split(':')
            if len(ppaths) == 2 and len(model_name) > 0:
                ppath_value = ppaths[1]
                model_path_dict[model_name] = ppath_value

    for model_name in model_path_dict.keys():
        parseData(model_name, model_path_dict.get(model_name), 0)
        sleep(random.randint(1,5))




def parseData(model_name, ppath_value, cursor):
    data_url_tmplate = f'https://s.taobao.com/search?q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190303&ie=utf8&cps=yes&ppath={ppath_value}&sort=sale-desc&bcoffset=0&p4ppushleft=%2C44&s={int(cursor)}'
    # data_url_tmplate = f'https://s.taobao.com/search?q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190303&ie=utf8&cps=yes&ppath=20000%3A654744979'
    browser.get(data_url_tmplate)

    # 下一页的游标
    next_page_classes = browser.find_elements_by_css_selector("[class='J_Ajax num icon-tag']")
    if len(next_page_classes) > 1:
        next_page_class = next_page_classes[1]
    else:
        next_page_class = next_page_classes[0]
        if next_page_class.get_attribute("trace") != 'srp_bottom_pagedown':
            next_page_class = None

    next_page_cursor = next_page_class.get_attribute("data-value") if next_page_class else None

    # 每页的44条数据
    watch_data_list = browser.find_elements_by_css_selector("[class='ctx-box J_MouseEneterLeave J_IconMoreNew']")
    for watch_data_raw in watch_data_list:
        watch_data = {}
        watch_data_html = BeautifulSoup(watch_data_raw.get_attribute("outerHTML"), features="html.parser")

        # 设备id
        item_id = watch_data_html.find(name='a', attrs={"class": "J_ClickStat"})["trace-nid"]
        watch_data['item_id'] = item_id

        if len(list(client.watch_deal_cnt_collection.find({"item_id": item_id}))) > 0:
            print(f'model={model_name} : item={item_id} exists')
            continue
        # 销量
        deal_cnt = watch_data_html.find(name='div', attrs={"class": "deal-cnt"}).text
        watch_data['deal_cnt'] = int(deal_cnt[0:-3])
        # 价格
        price = watch_data_html.find(name='div', attrs={"class": "price g_price g_price-highlight"}).text
        watch_data['price'] = price.strip()
        watch_data['price'] = price.strip() if price else None
        # 设备名称
        item_name = watch_data_html.find(name='a', attrs={"class": "J_ClickStat"}).text
        watch_data['item_name'] = item_name.strip() if item_name else None
        # 店铺名称
        shop_name = watch_data_html.find(name='a', attrs={"class": "shopname J_MouseEneterLeave J_ShopInfo"}).text
        watch_data['shop_name'] = shop_name.strip() if shop_name else None
        # 店铺位置
        shop_location = watch_data_html.find(name='div', attrs={"class": "location"}).text
        watch_data['shop_location'] = shop_location

        watch_data['model_name'] = model_name

        client.watch_deal_cnt_collection.insert_one(watch_data)

        sleep(random.randint(1,2))
        print(f'666666-model={model_name}; cursor={next_page_cursor}; item_id={item_id} done')

    if next_page_cursor:
        parseData(model_name, ppath_value, int(next_page_cursor))
        sleep(random.randint(1, 5))




if __name__ == "__main__":
    # parse()
    init()
    # initBrowser()
    # initCookie()
    parseModel()