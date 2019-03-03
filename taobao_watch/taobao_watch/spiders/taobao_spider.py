import json
import re
from datetime import time
from time import sleep

import scrapy
import zol_watch.util.client as client
from bs4 import BeautifulSoup
from selenium import webdriver

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
    name = 'taobao_watch'

    brand_index = 0
    client.init_mongodb_conn()

    # 爬虫允许的域名
    allowed_domains = ['taobao.com', 'passport.alibaba.com']
    # 爬虫进行模拟登录的url
    login_url = 'https://login.taobao.com/member/login.jhtml'


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'Keep-Alive'
    }

    # 模拟登录需要提交的用户名
    username = '13681263532'
    # 构建模拟登录需要提交的表单数据
    post_data = {
        'TPL_username': username,
        'TPL_password': 'xlchen6b40810@',
        'ncoSig': '',
        'ncoSessionid': '',
        'ncoToken': 'd801d3c69349',
        'slideCodeShow': 'false',
        'useMobile': 'false',
        'lang': 'zh_CN',
        'loginsite': '0',
        'newlogin': '0',
        'TPL_redirect_url': 'http://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?spm=a1z02.1.a2109.d1000368.5d3a782dr6KjrH&nekot=1470211439694',
        'from': 'tb',
        'fc': 'default',
        'style': 'default',
        'css_style': '',
        'keyLogin': 'false',
        'qrLogin': 'true',
        'newMini': 'false',
        'newMini2': 'false',
        'tid': '',
        'loginType': '3',
        'minititle': '',
        'minipara': '',
        'pstrong': '',
        'sign': '',
        'need_sign': '',
        'isIgnore': '',
        'full_redirect': '',
        'sub_jump': '',
        'popid': '',
        'callback': '',
        'guf': '',
        'not_duplite_str': '',
        'need_user_id': '',
        'poy': '',
        'gvfdcname': '10',
        'gvfdcre': '68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61317A30392E322E37353438',
        'from_encoding': '',
        'sub': '',
        'TPL_password_2': '9b8f47092a216b0df4f68ee751c65ba430627e81b09029f29be8d6d1e24b62b8338222b95e759f9877f0051e096ae285181621f1',
        'loginASR': '1',
        'loginASRSuc': '1',
        'allp': '',
        'oslanguage': 'zh-CN',
        'sr': '1920*1080',
        'osVer': 'windows|6.1',
        'naviVer': 'chrome|67.0339687',
        'osACN': 'Mozilla',
        'osAV': '5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        'osPF': 'Win32',
        'miserHardInfo': '',
        'appkey': '00000000',
        'nickLoginLink': '',
        'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=http://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?spm=a1z02.1.a2109.d1000368.5d3a782dr6KjrH&nekot=1470211439694&useMobile=true',
        'showAssistantLink': '',
        'um_token': 'HV02PAAZ0bb0767c3af',
        'ua': 'rQcXNgSTHZhdvYEp94Q9LWm3tf/rWXTklo5KCcpiO9WwblFoikTWZTfZQ7wfTsnnTb8z6gm8TsTTJ7ZyUxxBEdKEiqnZosTTb8r26zmTnsZwpPVsSHbFSbBM/qwfzTTBrT5S6K+aTjsnj6UfP/T2Tj+teh9f8plTIb826zmgsjTQTVj1vhovBOLEukvAHyptk38gOP4Tth2VR3CpC+jJ+IPZXx71zeO8I8'

    }


    def start_requests(self):  # 由此方法通过下面链接爬取页面

        yield scrapy.Request(
            url=self.login_url,
            meta={'cookiejar': 1},
            headers=self.headers,
            callback=self.post_login
        )

        # # 定义爬取的链接：搜索"智能手表"的结果页
        # urls = [
        #     'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest'
        # ]
        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse, cookies=cookie_str)  # 爬取到的页面如何处理？提交给parse方法处理


    def post_login(self, response):
        yield scrapy.FormRequest.from_response(
            response=response,
            method='POST',
            meta={'cookiejar': response.meta['cookiejar']},
            formdata=self.post_data,
            callback=self.search_token,
            dont_filter=True
        )

    # 登录成功后， 获取token值拼接url进行请求，跳过验证
    def search_token(self, response):

        data0 = str(response.body)
        # token0 = re.search(r'&token=.*?&', data0)
        # data1 = token0.group()
        # token1 = re.sub(r'&', '', data1)
        # token2 = re.sub(r'token=', '', token1)

        nekot0 = re.search(r'&nekot=.*?}', data0)
        data1 = nekot0.group()
        nekot1 = re.sub(r'&', '', data1)
        nekot2 = re.sub(r'nekot=', '', nekot1)
        nekot3 = re.sub(r'\'}', '', nekot2)
        nekot4 = re.sub(r'\\', '', nekot3)
        token_URL = 'https://passport.alibaba.com/mini_apply_st.js?site=0&token=%s&callback=stCallback6' % nekot4

        yield scrapy.Request(
            url=token_URL,
            meta={'cookiejar': response.meta['cookiejar']},
            headers=self.headers,
            callback=self.parse_crawl_url
        )

    def parse_crawl_url(self, response):

        # 爬虫要抓取数据的url
        crawl_urls = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%99%BA%E8%83%BD%E6%89%8B%E8%A1%A8&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest'

        yield scrapy.Request(
            meta={'cookiejar': response.meta['cookiejar']},
            url=crawl_urls,
            headers=self.headers,
            callback=self.parse
        )



    # 循环品牌列表
    def parse(self, response):
        # 调试用
        homepage = response.body
        # 取出品牌名称及id

        watch_brand_raw = response.css("#manuSer").extract()


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
