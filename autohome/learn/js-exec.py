import re
# import PyV8
import logging
import requests

import execjs

def clscontent(alljs):
    try:
        # ctx = PyV8.JSContext()
        # ctx.enter()
        # ctx.eval(alljs)
        # return .eval('rules')
        cts = execjs.compile(alljs)
        return cts.call('createElement')
    except:
        logging.exception('clscontent function exception')
        return None

def makejs(html):
    try:
        alljs = ("var rules = '';"
                 "var document = {};"
                 "document.createElement = function() {"
                 "      return {"
                 "              sheet: {"
                 "                      insertRule: function(rule, i) {"
                 "                              if (rules.length == 0) {"
                 "                                      rules = rule;"
                 "                              } else {"
                 "                                      rules = rules + '#' + rule;"
                 "                              }"
                 "                      }"
                 "              }"
                 "      }"
                 "};"
                 "document.querySelectorAll = function() {"
                 "      return {};"
                 "};"
                 "document.head = {};"
                 "document.head.appendChild = function() {};"

                 "var window = {};"
                 "window.decodeURIComponent = decodeURIComponent;")

        js = re.findall('(\(function\([a-zA-Z]{2}.*?_\).*?\(document\);)', html)
        for item in js:
            alljs = alljs + item
        return alljs
    except:
        logging.exception('makejs function exception')
        return None

def main(index):
    try:
        req = requests.get('https://car.autohome.com.cn/config/series/%d.html' % index)
        alljs = makejs(req.text)
        if(alljs == None):
            print('makejs error')
            return

        result = clscontent(alljs)
        if(result == None):
            print('clscontent error')
            return

        for item in result.split('#'):
            print(item)
    except:
        logging('main function exception')

if __name__ == '__main__':
    main(153)

    script = "return window.getComputedStyle(document.getElementsByClassName('" + classname + "')[0], 'before').getPropertyValue('content')"
    pseudo_element_content = driver.execute_script(script)