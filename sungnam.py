#!/usr/bin/env python
#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common import exceptions
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

WAITING_TIME_FOR_LOGIN = 30 # 로그인을 기다리는 시간
NUMBER_OF_TARET_WEEKS = 5 # 현재 날짜 기준 몇주(week)를 대상으로 잡을지
#TARGET_DAY = 'sun'
TARGET_DAY = 'sat' # 요일
TRY_TO_CATCH_INTERVAL = 60 # 자리 확보시 몇초 간격으로
MAX_TRY_TO_CATCH_A_SEAT = 60*24 # 최대 몇번 다시 잡을지 (세션 유지를 위해)
LOGIN_URL = "https://ticket.interpark.com/Gate/TPLogin.asp?CPage=B&MN=Y&tid1=main_gnb&tid2=right_top&tid3=login&tid4=login"

chrome_options = Options()
#chrome_options.add_argument('--kiosk')

browser = webdriver.Chrome(executable_path="chromedriver.exe",
                           options=chrome_options)
browser.set_window_size(1600,900)


def main():
    if login():
        check_bookable()


def login():
    # 인터파크 로그인
    browser.get(LOGIN_URL)
    browser.execute_script("snsAuthPopup('naver');")
    time.sleep(3)

    # browser.switch_to.window('popup')
    # time.sleep(WAITING_TIME_FOR_LOGIN)
    # browser.switch_to.window('diams')
    try:
        WebDriverWait(browser, WAITING_TIME_FOR_LOGIN).until(EC.url_changes(LOGIN_URL))
        return True
    except exceptions.TimeoutException:
        print(str(WAITING_TIME_FOR_LOGIN) + "초 안에 로그인되지 않음")
        return False


def check_bookable():
    while 1:
        browser.get("http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?GoodsCode=14009928")
        time.sleep(1)

        browser.execute_script("fnPlayDateTab(1);")
        time.sleep(1)

        try:
            div_play_date_list = browser.find_elements_by_css_selector(
                'div#divPlayDateList.Date_list ul.area li a.' + TARGET_DAY)
        except exceptions.NoSuchElementException:
            break

        idx_target_weeks = 0

        skip_check_next_week = False

        for play_date in div_play_date_list:
            idx_target_weeks = idx_target_weeks + 1

            if idx_target_weeks > NUMBER_OF_TARET_WEEKS or skip_check_next_week is True:
                break

            print(play_date.text + ' click')
            play_date.click()
            time.sleep(1)

            browser.execute_script("$('ul#ulPlaySeq.iList li label')[1].click()")
            time.sleep(1)

            try:
                result_text = browser.find_element_by_css_selector('ul#ulSeatList li').text
            except exceptions.NoSuchElementException:
                break

            if result_text and result_text.find('매진') != -1:
                 print(play_date.text + ' ' + result_text)
            else:
                 print(play_date.text + ' ' + result_text)
                 print('NEED TO CALL REST API!!')

                 try:
                     ul_play_seq_list = browser.find_elements_by_css_selector('ul#ulPlaySeq.iList li label')
                 except exceptions.NoSuchElementException:
                     break

                 for play_seq in ul_play_seq_list:
                    if play_seq.get_property('innerText').find('1박 2일') != -1:
                        print('1박 2일 click')

                        try:
                            play_seq.click()
                        except exceptions.ElementNotVisibleException:
                            browser.execute_script("$('ul#ulPlaySeq.iList li label')[1].click()")
                        time.sleep(1)

                        try:
                            print('예약하기 click')
                            browser.find_element_by_css_selector('a.btn_booking').click()
                        except exceptions.NoSuchElementException:
                            break
                        time.sleep(1)

                        # 윈도우 전환
                        browser.switch_to.window('wndBooking')
                        time.sleep(1)
                        browser.execute_script("fnBookNoticeShowHide('');")
                        time.sleep(1)

                        browser.switch_to.default_content()
                        browser.switch_to.frame('ifrmSeat')
                        time.sleep(1)
                        browser.find_elements_by_css_selector('area')[0].click()
                        time.sleep(1)

                        sty_seat_list = browser.find_elements_by_css_selector('img.stySeat')
                        if sty_seat_list.__len__() > 0:
                            print(sty_seat_list[0].get_attribute('alt') + ' check!')
                            sty_seat_list[0].click()
                        else:
                            print('CANNOT SELECT A SEAT.. T^T')
                            browser.switch_to.default_content()
                            # 윈도우 복귀
                            browser.execute_script("window.close()")
                            browser.switch_to.window('diams')
                            break

                        time.sleep(1)
                        browser.execute_script("fnSelect();")
                        time.sleep(1)
                        print('CATCH A SEAT!')

                        # 잡은 자리를 TRY_TO_CATCH_INTERVAL 초 간격으로 놓았다가 다시 잡음
                        # 총 MAX_TRY_TO_CATCH_A_SEAT 회
                        count_catch_a_seat = 0

                        while 1:
                            count_catch_a_seat = count_catch_a_seat + 1

                            # uncheck seat
                            time.sleep(TRY_TO_CATCH_INTERVAL)

                            browser.switch_to.default_content()
                            browser.execute_script("fnPrevStep()")
                            time.sleep(1)

                            browser.switch_to.default_content()
                            browser.switch_to.frame('ifrmSeat')

                            sty_select_seat_list = browser.find_elements_by_css_selector('img.stySelectSeat')
                            print(sty_select_seat_list[0].get_attribute('alt') + ' uncheck!')
                            sty_select_seat_list[0].click()
                            time.sleep(1)

                            # check to re-check seat or not
                            if count_catch_a_seat > MAX_TRY_TO_CATCH_A_SEAT:
                                print('RELEASE A SEAT')
                                skip_check_next_week = True
                                browser.switch_to.default_content()
                                break

                            # re-check seat
                            sty_seat_list = browser.find_elements_by_css_selector('img.stySeat')
                            if sty_seat_list.__len__() > 0:
                                print(sty_seat_list[0].get_attribute('alt') + ' re-check!')
                                sty_seat_list[0].click()
                            else:
                                print('CANNOT SELECT A SEAT.. T^T, RETRY COUNT = '
                                      + str(count_catch_a_seat))
                                skip_check_next_week = False
                                browser.switch_to.default_content()
                                break

                            time.sleep(1)
                            browser.execute_script("fnSelect();")
                            time.sleep(1)
                            print('RE-CATCH A SEAT!!, RETRY COUNT = ' + str(count_catch_a_seat))
                            browser.switch_to.default_content()

                        # 윈도우 복귀
                        browser.execute_script("window.close()")
                        browser.switch_to.window('diams')
                        break
                    else:
                        print(play_seq.get_property('innerText'))
                        continue

main()
browser.quit()
