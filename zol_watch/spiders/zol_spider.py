import json
from datetime import time

import scrapy
import zol_watch.util.client as client
from bs4 import BeautifulSoup

class autohome(scrapy.Spider):
    name = 'zol_watch'

    brand_index = 0
    client.init_mongodb_conn()

    def start_requests(self):  # 由此方法通过下面链接爬取页面

        # 定义爬取的链接
        urls = [
            'http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1.html'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)  # 爬取到的页面如何处理？提交给parse方法处理

    # 循环品牌列表
    def parse(self, response):
        # 调试用
        homepage = response.body
        # 按id取出元素列表-品牌列表元素数据
        watch_brand_raw = response.css("#manuSer").extract()
        watch_brand_html = BeautifulSoup(watch_brand_raw[0], features="html.parser")
        # 提取lable
        car_brand_label_list = watch_brand_html.find_all("label")
        # todo: 修改数量限定
        for car_brand_label in car_brand_label_list:
            watch_brand_name = car_brand_label.attrs['title']
            watch_brand_input_list = car_brand_label.find_all("input")
            if len(watch_brand_input_list) == 0:
                continue
            watch_brand_input = watch_brand_input_list[0]
            watch_brand_id = watch_brand_input.attrs["value"]
            query_brand_url = f'http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1_{watch_brand_id}_1_1_0_1.html?#showc'
            self.brand_index += 1
            print("------------", self.brand_index)
            yield scrapy.Request(url=query_brand_url, callback=self.parse_watch_page_of_brand, meta={'watch_branch_name': watch_brand_name, 'watch_branch_id': watch_brand_id})

    # 提取某品牌下手表的总页数比循环遍历
    def parse_watch_page_of_brand(self, response):
        watch_brand_name = response.meta['watch_branch_name']
        watch_brand_id = response.meta['watch_branch_id']

        if watch_brand_id == "m544" or watch_brand_id == "m613":
            print("oooooooo")

        watch_info_list = self.get_device_list(response, watch_brand_id, watch_brand_name)
        if len(watch_info_list) > 0:
            for watch_info in watch_info_list:
                query_detail_url = f'http://detail.zol.com.cn' + watch_info["watch_url"]
                yield scrapy.Request(url=query_detail_url, callback=self.parse_detail_info,
                                     meta={'watch_info': watch_info})

        total_page = self.get_total_page(response)
        if total_page < 2:
            return
        for page in range(total_page):
            if page == 0:
                continue
            page = page+1
            query_watch_url = f'http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1_{watch_brand_id}_1_1_0_{page}.html?#showc'
            yield scrapy.Request(url=query_watch_url, callback=self.parse_watch_info,
                                 meta={'watch_branch_name': watch_brand_name, 'watch_branch_id': watch_brand_id})

    def parse_watch_info(self, response):
        # 调试用
        car_model_raw = response.body
        watch_brand_name = response.meta['watch_branch_name']
        watch_brand_id = response.meta['watch_branch_id']

        if watch_brand_id == "m544" or watch_brand_id == "m613":
            print("oooooooo")

        watch_info_list = self.get_device_list(response, watch_brand_id, watch_brand_name)
        if len(watch_info_list) > 0:
            for watch_info in watch_info_list:
                query_detail_url = f'http://detail.zol.com.cn' + watch_info["watch_url"]
                yield scrapy.Request(url=query_detail_url, callback=self.parse_detail_info,
                                     meta={'watch_info': watch_info})

    def parse_detail_info(self, response):
        # 调试用
        raw = response.body
        watch_info = response.meta['watch_info']
        watch_config_json = {}
        watch_config_list_raw = response.css(".section-content").extract()
        if len(watch_config_list_raw) > 0:
            for watch_config_raw in watch_config_list_raw:
                watch_config_html = BeautifulSoup(watch_config_raw, features="html.parser")
                watch_config_item_list = watch_config_html.findAll("li")
                if len(watch_config_item_list) == 0 :
                    continue
                for watch_config_item in watch_config_item_list:
                    watch_config_list = watch_config_item.findAll("p")
                    if len(watch_config_list) == 0 :
                        continue
                    for watch_config in watch_config_list:
                        config = watch_config.text.split("：")
                        if len(config) == 2:
                            watch_config_json[config[0]] = config[1]
        watch_info["main_config"] = watch_config_json
        item = client.zol_config_collection.find({"watch_id": watch_info["watch_id"]})
        if len(list(item)) > 0:
            return
        client.zol_config_collection.insert_one(watch_info)
        print(watch_info)

    def get_device_list(self, response, watch_brand_id, watch_brand_name):
        watch_info_list = []
        watch_device_raw = response.css("#result_box").extract()
        watch_device_html = BeautifulSoup(watch_device_raw[0], features="html.parser")

        watch_device_list = watch_device_html.findAll(name='dl', attrs={"class": "pro_detail"})
        if len(watch_device_list) == 0:
            return
        for watch_device in watch_device_list:
            watch_info = {}
            watch_name = watch_device.find("dt").text
            watch_id = watch_device.find("dt").find("a").attrs["id"]
            watch_url = watch_device.find("dt").find("a").attrs["href"]
            watch_info["watch_brand_id"] = watch_brand_id
            watch_info["watch_brand_name"] = watch_brand_name
            watch_info["watch_id"] = watch_id
            watch_info["watch_name"] = watch_name
            watch_info["watch_url"] = watch_url
            watch_info_list.append(watch_info)
        return watch_info_list


    def get_total_page(self, response):
        try:
            watch_device_raw = response.css("#result_box").extract()
            watch_device_html = BeautifulSoup(watch_device_raw[0], features="html.parser")
            page_info_raw_list = watch_device_html.findAll(name='p', attrs={"class": "page_order"})
            if len(page_info_raw_list) == 0:
                return 0
            page_info_raw = page_info_raw_list[0]
            total_page = int(page_info_raw.text[:5].split("/")[1])
        except:
            print("111111111111", str(page_info_raw))
        return total_page
