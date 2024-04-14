from selenium import webdriver
from selenium.webdriver.edge.service import Service

import time
import os
import downloaddriver as dd


def check_cookie(cookies):
    for cookie in cookies:

        if cookie['name'] == 'insert_cookie':
            insert_cookie = cookie['value']
        if cookie['name'] == 'iPlanetDirectoryPro':
            iPlanetDirectoryPro = cookie['value']
        if cookie['name'] == 'JSESSIONID' and cookie['path'] == '/':
            JSESSIONID = cookie['value']

    try:
        return JSESSIONID, insert_cookie, iPlanetDirectoryPro
    except:
        return '', '', ''



class GetCookie:
    def __init__(self):
        ser = Service()
        if not os.path.exists("./edgedriver_win64/msedgedriver.exe"):
            dd.download_driver()
        ser.path = './edgedriver_win64/msedgedriver.exe'
        browser = webdriver.Edge(service=ser)
        url = 'https://ugsqs.whu.edu.cn/new/student/'

        browser.get(url)
        cookies = browser.get_cookies()

        # print(browser.current_url.split('/')[2])
        while browser.current_url.split('/')[2] == 'cas.whu.edu.cn':
            time.sleep(1)
            pass

        cookies = browser.get_cookies()
        print(cookies)
        self.JSESSIONID, self.insert_cookie, self.iPlanetDirectoryPro = check_cookie(cookies)



# c = GetCookie()
