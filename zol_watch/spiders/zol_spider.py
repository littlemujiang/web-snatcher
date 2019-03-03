import json
from datetime import time

import scrapy
import zol_watch.util.client as client
from bs4 import BeautifulSoup

'''
整体流程：
1. 从http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1.html进入，获取到手表的全部型号（id），
2. 拼接url: http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1_{watch_brand_id}_1_1_0_1.html?#showc，遍历每个型号
3. 在此页面，查出第1页的全部手表以及总页数，如果多于1页，则修改页码（_1_1_0_{页码}.html），查询后面页码下的全部手表
4. 对全部手表进行遍历，根据id拼接url：http://detail.zol.com.cn' + watch_info["watch_url"]
5. 查出每个手表的配置信息
6. 入库
'''

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
        # 遍历品牌列表
        for car_brand_label in car_brand_label_list:
            watch_brand_name = car_brand_label.attrs['title']
            watch_brand_input_list = car_brand_label.find_all("input")
            if len(watch_brand_input_list) == 0:
                continue
            watch_brand_input = watch_brand_input_list[0]
            # 取出品牌id，嵌入url
            watch_brand_id = watch_brand_input.attrs["value"]
            query_brand_url = f'http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1_{watch_brand_id}_1_1_0_1.html?#showc'
            self.brand_index += 1
            print("------------", self.brand_index)
            yield scrapy.Request(url=query_brand_url, callback=self.parse_watch_page_of_brand, meta={'watch_branch_name': watch_brand_name, 'watch_branch_id': watch_brand_id})

    # 提取某品牌下手表的全部设备并循环遍历
    def parse_watch_page_of_brand(self, response):
        watch_brand_name = response.meta['watch_branch_name']
        watch_brand_id = response.meta['watch_branch_id']

        # 获取到第一页的手表数据
        watch_info_list = self.get_device_list(response, watch_brand_id, watch_brand_name)
        if len(watch_info_list) > 0:
            # 遍历第一页的手表
            for watch_info in watch_info_list:
                query_detail_url = f'http://detail.zol.com.cn' + watch_info["watch_url"]
                yield scrapy.Request(url=query_detail_url, callback=self.parse_detail_info,
                                     meta={'watch_info': watch_info})

        # 解析出此品牌下手表的页数
        total_page = self.get_total_page(response)
        if total_page < 2:
            return
        # 如果页数超过1页，则需要对后面的页做解析
        for page in range(total_page):
            # 第1页的手表在上面已经解析，所以跳过
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
        # 取出此页面的手表列表
        watch_info_list = self.get_device_list(response, watch_brand_id, watch_brand_name)
        if len(watch_info_list) > 0:
            # 遍历手表列表，获取手表的详细信息
            for watch_info in watch_info_list:
                query_detail_url = f'http://detail.zol.com.cn' + watch_info["watch_url"]
                yield scrapy.Request(url=query_detail_url, callback=self.parse_detail_info,
                                     meta={'watch_info': watch_info})
    # 解析手表的详细信息
    def parse_detail_info(self, response):
        # 调试用
        raw = response.body
        watch_info = response.meta['watch_info']
        watch_config_json = {}
        watch_config_list_raw = response.css(".section-content").extract()
        if len(watch_config_list_raw) > 0:
            # 某个手表的原始配置信息
            for watch_config_raw in watch_config_list_raw:
                watch_config_html = BeautifulSoup(watch_config_raw, features="html.parser")
                watch_config_item_list = watch_config_html.findAll("li")
                if len(watch_config_item_list) == 0 :
                    continue
                #  遍历4类配置
                for watch_config_item in watch_config_item_list:
                    watch_config_list = watch_config_item.findAll("p")
                    if len(watch_config_list) == 0 :
                        continue
                    # 遍历每类配置下的2个配置，并解析
                    for watch_config in watch_config_list:
                        config = watch_config.text.split("：")
                        if len(config) == 2:
                            watch_config_json[config[0]] = config[1]
        # 查询完成，组装，入库
        watch_info["main_config"] = watch_config_json
        item = client.zol_config_collection.find({"watch_id": watch_info["watch_id"]})
        if len(list(item)) > 0:
            return
        client.zol_config_collection.insert_one(watch_info)
        print(watch_info)

    # 从页面中获取手表列表
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

    # 从页面中获取总页数
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
