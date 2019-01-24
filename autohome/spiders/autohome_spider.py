import json

import scrapy

import autohome.spiders.autohome_config_parser as config_parser
import util.client as client

class autohome(scrapy.Spider):
    name = 'autohome'

    client.init_mongodb_conn()

    def start_requests(self):  # 由此方法通过下面链接爬取页面

        # 定义爬取的链接
        urls = [
            'https://car.autohome.com.cn/javascript/NewSpecCompare.js?20131010'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)  # 爬取到的页面如何处理？提交给parse方法处理

    def parse(self, response):
        query_model_base_url = 'https://car.autohome.com.cn/duibi/ashx/specComparehandler.ashx?callback=jQuery112401755185345933663_1540644205221&type=1&seriesid='
        car_brand_raw = response.body
        car_brand_list_str = str(car_brand_raw, encoding='gbk')[21:-3]
        car_brand_list = json.loads(car_brand_list_str)
        for car_brand in car_brand_list:
            car_series_data = {}
            car_brand_index = car_brand['L']
            car_brand_name = car_brand['N']
            car_series_data['car_brand_index'] = car_brand_index
            car_series_data['car_brand_name'] = car_brand_name
            car_series_info_list = car_brand['List']
            if(len(car_series_info_list) > 0):
                for car_series_info in car_series_info_list:
                    car_series_list = car_series_info['List']
                    if(len(car_series_list) > 0 ):
                        for car_series in car_series_list:
                            # car_series = car_series_list[0]
                            car_series_id = car_series['I']
                            # car_series_name = car_series['N']
                            # car_series_data['car_series_id'] = car_series_id
                            # car_series_data['car_series_name'] = car_series_name
                            query_model_url = query_model_base_url + str(car_series_id)
                            yield scrapy.Request(url=query_model_url, callback=self.parse_model,  meta={'car_series_data': car_series_data,'car_series': car_series})


    def parse_model(self, response):
        car_series_data = response.meta['car_series_data']
        car_series = response.meta['car_series']

        car_series_id = car_series['I']
        car_series_name = car_series['N']
        car_series_data['car_series_id'] = car_series_id
        car_series_data['car_series_name'] = car_series_name

        car_model_raw = response.body
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


