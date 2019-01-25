import json

import scrapy

import zol_watch.spiders.zol_config_parser as config_parser
import zol_watch.util.client as client
from bs4 import BeautifulSoup

class autohome(scrapy.Spider):
    name = 'zol_watch'

    client.init_mongodb_conn()

    def start_requests(self):  # 由此方法通过下面链接爬取页面

        # 定义爬取的链接
        urls = [
            'http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1.html'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)  # 爬取到的页面如何处理？提交给parse方法处理

    def parse(self, response):
        query_model_base_url = 'https://car.autohome.com.cn/duibi/ashx/specComparehandler.ashx?callback=jQuery112401755185345933663_1540644205221&type=1&seriesid='
        homepage = response.body
        watch_brand_raw = response.css("#manuSer").extract()
        watch_brand_html = BeautifulSoup(watch_brand_raw[0], features="html.parser")
        car_brand_label_list = watch_brand_html.find_all("label")
        for car_brand_label in car_brand_label_list:
            watch_brand_name = car_brand_label.attrs['title']
            watch_brand_input_list = car_brand_label.find_all("input")
            if len(watch_brand_input_list) == 0:
                continue
            watch_brand_input = watch_brand_input_list[0]
            watch_brand_id = watch_brand_input.attrs["value"]
            query_brand_url = f'http://detail.zol.com.cn/GPSwatch_advSearch/subcate827_1_{watch_brand_id}_1_1_0_1.html?#showc'
            yield scrapy.Request(url=query_brand_url, callback=self.parse_model,  meta={'watch_branch_name': watch_brand_name,'watch_branch_id': watch_brand_id})


    def parse_model(self, response):
        watch_branch_name = response.meta['watch_branch_name']
        watch_branch_id = response.meta['watch_branch_id']

        car_model_raw = response.body
        watch_device_raw = response.css("#result_box").extract()
        watch_device_html = BeautifulSoup(watch_device_raw[0], features="html.parser")
        watch_device_list = watch_device_html.findAll(name='dl',attrs={"class":"pro_detail"})
        car_model_list_str_raw = str(car_model_raw, encoding='gbk')
        index = car_model_list_str_raw.find('(')
        car_model_list_str = car_model_list_str_raw[index+1:-1]
        car_model_list_info = json.loads(car_model_list_str)
        # print(car_model_list['I'])
        car_model_list_all = car_model_list_info['List']
        if(len(car_model_list_all) > 0):
            car_model_info_onsale = car_model_list_all[0]
            car_model_list = car_model_info_onsale['List']
            car_model = car_model_list[0]
            car_model_id = car_model['I']
            car_model_name = car_model['N']
            car_series_data['car_model_id'] = car_model_id
            car_series_data['car_model_name'] = car_model_name
            if len(list(client.car_config_collection.find({"car_model_id": car_model_id}))) > 0:
                print(str(car_model_name) + '已经存在')
                return
            yield config_parser.get_config_data_by_id(car_model_id, car_series_data)
            # query_config_url = f'https://car.autohome.com.cn/config/spec/{car_model_id}.html'
            # yield scrapy.Request(url=query_config_url, callback=self.parse_info)
            # yield scrapy_splash.SplashRequest(url=query_config_url,callback=self.parse_info)


