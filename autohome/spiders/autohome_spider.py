import json

import scrapy
# import scrapy_splash


class autohome(scrapy.Spider):
    name = 'autohome'

    def start_requests(self):  # 由此方法通过下面链接爬取页面

        # 定义爬取的链接
        urls = [
            # 'http://lab.scrapyd.cn/page/1/',
            # 'http://lab.scrapyd.cn/page/2/',
            'https://car.autohome.com.cn/javascript/NewSpecCompare.js?20131010'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)  # 爬取到的页面如何处理？提交给parse方法处理


    def parse(self, response):
        '''
        start_requests已经爬取到页面，那如何提取我们想要的内容呢？那就可以在这个方法里面定义。
        这里的话，并木有定义，只是简单的把页面做了一个保存，并没有涉及提取我们想要的数据，后面会慢慢说到
        也就是用xpath、正则、或是css进行相应提取，这个例子就是让你看看scrapy运行的流程：
        1、定义链接；
        2、通过链接爬取（下载）页面；
        3、定义规则，然后提取数据；
        就是这么个流程，似不似很简单呀？
        '''

        query_model_base_url = 'https://car.autohome.com.cn/duibi/ashx/specComparehandler.ashx?callback=jQuery112401755185345933663_1540644205221&type=1&seriesid='

        car_brand_raw = response.body
        car_brand_list_str = str(car_brand_raw, encoding='gbk')[21:-3]
        car_brand_list = json.loads(car_brand_list_str)

        for car_brand in car_brand_list:
            car_series_info_list = car_brand['List']
            if(len(car_series_info_list) > 0):
                for car_series_info in car_series_info_list:
                    car_series_list = car_series_info['List']
                    if(len(car_series_list) > 0 ):
                        for car_series in car_series_list:
                            car_series_id = car_series['I']
                            car_series_name = car_series['N']
                            query_model_url = query_model_base_url + str(car_series_id)
                            yield scrapy.Request(url=query_model_url, callback=self.parse_model)


    def parse_model(self, response):
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
            query_config_url = f'https://car.autohome.com.cn/config/spec/{car_model_id}.html'
            yield scrapy.Request(url=query_config_url, callback=self.parse_info)
            # yield scrapy_splash.SplashRequest(url=query_config_url,callback=self.parse_mode)

    def parse_info(self, response):
        car_config_raw = response.body
        car_config_str_raw = str(car_config_raw, encoding='gbk')
        mingyan_list = response.css('div.quote').extract()