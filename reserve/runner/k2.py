#!/usr/bin/env python
#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
import time, sys
from selenium.webdriver.common.action_chains import ActionChains
from multiprocessing import Queue


mobile_emulation = {
    "deviceMetrics": { "width": 360, "height": 900, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 BUILD/JOP400) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
}

chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

browser = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
browser.set_window_size(400, 940)

def main():
    while 1:
        time.sleep(1)

        browser.get("http://m.k2.co.kr/k2/ko/p/KMA13A05E7")
        time.sleep(2)

        browser.find_element_by_xpath("//select[@name='selProductSize']/option[text()='FREE(품절)']").click()
        time.sleep(2)

        try:
            browser.switch_to.alert.accept()
        except exceptions.NoAlertPresentException:
            print('재고 있음!! Need  to call API!!!')
        else:
            print('품절')
            browser.switch_to.default_content()


main()
browser.quit()
