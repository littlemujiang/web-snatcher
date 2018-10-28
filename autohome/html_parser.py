
from selenium import webdriver

if __name__ == "__main__":
    browser = webdriver.Chrome()
    # browser = webdriver.Firefox()

    browser.get("https://car.autohome.com.cn/config/spec/27911.html")

    # browser.switch_to.parent_frame()

    config_info = browser.find_element_by_id('tab_0')
    # text = browser.find_element_by_id('hs_kw14_configKs')
    # text_hide = browser.find_element_by_css_selector("span.hs_kw14_configKs")
    config_info_table_list = browser.find_element_by_class_name('tbcs')
    print(browser.find_element_by_id('config_data'))
    browser.close()