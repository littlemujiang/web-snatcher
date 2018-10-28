from pyquery import PyQuery as py
from selenium import webdriver

if __name__ == "__main__":
    browser = webdriver.Chrome()
    browser.get("https://car.autohome.com.cn/config/spec/27911.html")

    doc = py(browser.page_source)

    span = doc('span:contains(kw)')
    print(span)

