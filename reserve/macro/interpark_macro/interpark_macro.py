#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
import time


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from reserve.macro.reserve_macro import ReserveMacro


class InterparkMacro(ReserveMacro):
    WAITING_TIME_FOR_LOGIN = 60  # 로그인을 기다리는 시간 : 60
    NUMBER_OF_TARGET_WEEKS = 5  # 현재 날짜 기준 몇주(week)를 대상으로 잡을지 : 5
    TARGET_DAY = 'sat'  # 요일
    TRY_TO_CATCH_INTERVAL = 60  # 자리 확보시 몇초 간격으로 : 60
    MAX_TRY_TO_CATCH_A_SEAT = 180  # 최대 몇번 다시 잡을지 (세션 유지를 위해) : INTERVAL * 회수만큼의 시간 만큼 retry 됨
    LOGIN_URL = \
        "https://ticket.interpark.com/Gate/TPLogin.asp?CPage=B&MN=Y&tid1=main_gnb&tid2=right_top&tid3=login&tid4=login"
    RESERVE_RANGE = "1박 2일"

    def __init__(self, url: str, camp_name: str, telegram_token: str, telegram_chat_id: str,
                 target_day: str = TARGET_DAY, is_catch_a_seat: bool = True, exclude_keyword: str = "",
                 reserve_range: str = RESERVE_RANGE):
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')

        super().__init__(url, camp_name, telegram_token, telegram_chat_id, chrome_options)
        self.target_day = target_day
        self.is_catch_a_seat = is_catch_a_seat
        self.exclude_keyword = exclude_keyword
        self.reserve_range = reserve_range

    def _run(self):
        self._open_browser()
        if self.__login():
            self.__check_bookable()
        else:
            self.is_catch_a_seat = False
            self.__check_bookable()

    def _open_browser(self):
        super()._open_browser()
        self.browser.set_window_size(1600, 900)

    def __login(self):
        # 인터파크 로그인
        self.browser.get(self.LOGIN_URL)
        self.browser.execute_script("snsAuthPopup('naver');")
        time.sleep(3)

        # self.browser.switch_to.window('popup')
        # time.sleep(WAITING_TIME_FOR_LOGIN)
        # self.browser.switch_to.window(self.window_name)
        try:
            WebDriverWait(self.browser, self.WAITING_TIME_FOR_LOGIN).until(EC.url_changes(self.LOGIN_URL))
            return True
        except exceptions.TimeoutException:
            print(str(self.WAITING_TIME_FOR_LOGIN) + "초 안에 로그인되지 않음")
            return False

    def __check_bookable(self):
        while 1:
            try:
                # 상품으로 이동
                self.browser.get(self.url)
                time.sleep(1)

                # 달력에서 날짜 리스트 탭으로 변경
                self.browser.execute_script("fnPlayDateTab(1);")
                time.sleep(1)

                try:
                    div_play_date_list = self.browser.find_elements_by_css_selector(
                        'div#divPlayDateList.Date_list ul.area li a.' + self.target_day)
                except exceptions.NoSuchElementException as e:
                    raise e

                idx_target_weeks = 0

                # 날짜(요일) 선택
                for play_date in div_play_date_list:
                    idx_target_weeks = idx_target_weeks + 1

                    if idx_target_weeks > self.NUMBER_OF_TARGET_WEEKS:
                        break

                    print(play_date.text + ' click')
                    play_date.click()
                    time.sleep(1)

                    # 이용기간 선택 : 1박 2일
                    # self.browser.execute_script("$('ul#ulPlaySeq.iList li label')[1].click()")
                    # time.sleep(1)
                    try:
                        reserve_range_list: list = self.browser.find_elements_by_css_selector(
                            'ul#ulPlaySeq.iList li label')
                    except exceptions.NoSuchElementException as e:
                        raise e

                    reserve_range_idx = 0
                    for reserve_range in reserve_range_list:
                        if reserve_range.get_property('innerText').find(self.reserve_range) > 0:
                            self.browser.execute_script("$('ul#ulPlaySeq.iList li label')[{idx}].click()".format(
                                idx=reserve_range_idx
                            ))
                            time.sleep(1)
                            break
                        reserve_range_idx += 1

                    product_group_list: list = self.browser.find_elements_by_css_selector('ul#ulSeatList li')
                    product_group_idx = -1
                    for product_group in product_group_list:
                        product_group_idx += 1
                        try:
                            product_group_text = product_group.text
                        except exceptions.NoSuchElementException as e:
                            raise e

                        if not product_group_text:
                            print("product_group_text is EMPTY!!!")
                            continue

                        exclude_keyword_list: [str] = self.exclude_keyword.split('|')

                        if self.__is_exclude(exclude_keyword_list, product_group_text):
                            continue

                        if product_group_text.find('매진') != -1:
                            print(play_date.text + ' ' + product_group_text)
                        else:
                            print(play_date.text + ' ' + product_group_text)
                            message = "======= {} ======= \n" \
                                      "{} {} 예약가능\n" \
                                      "--------------------------\n" \
                                      "{}" \
                                      "==========================".format(self.camp_name, play_date.text,
                                                                          product_group_text, self.url)
                            self.telegram_util.send_message(message)

                            if self.is_catch_a_seat:
                                self.__catch_a_seat(product_group_idx)

            except Exception as e:
                # 팝업 관련 에러인 경우 대비하여 기존 윈도우로 전환
                self.browser.switch_to.window(self.window_name)
                time.sleep(1)
                raise e

    def __catch_a_seat(self, product_group_idx: int):
        # 예약 팝업 띄우기
        try:
            print('예약하기 click')
            self.browser.find_element_by_css_selector('a.btn_booking').click()
        except exceptions.NoSuchElementException:
            raise Exception("예약하기 버튼 클릭 실패(팝업)")

        time.sleep(1)

        # 팝업으로 전환
        self.browser.switch_to.window('wndBooking')

        # 팝업 내 공지 사항 닫기
        time.sleep(1)
        self.browser.execute_script("fnBookNoticeShowHide('');")
        time.sleep(1)

        # 팝업 내 iframe 으로 전환
        self.browser.switch_to.default_content()
        self.browser.switch_to.frame('ifrmSeat')
        time.sleep(1)

        # area 선택
        area_list: list = self.browser.find_elements_by_css_selector('area')

        area_list[product_group_idx].click()
        time.sleep(1)

        # 자리 선택
        sty_seat_list = self.browser.find_elements_by_css_selector('img.stySeat')
        if sty_seat_list.__len__() > 0:
            print(sty_seat_list[0].get_attribute('alt') + ' check!')
            sty_seat_list[0].click()
        else:
            print('CANNOT SELECT A SEAT.. T^T')
            self.browser.switch_to.default_content()

            # 윈도우 복귀
            self.browser.execute_script("window.close()")
            self.browser.switch_to.window(self.window_name)

            time.sleep(1)
            return
        
        self.browser.execute_script("fnSelect();")
        time.sleep(1)
        print('CATCH A SEAT!')

        # 잡은 자리를 TRY_TO_CATCH_INTERVAL 초 간격으로 놓았다가 다시 잡음
        # 총 MAX_TRY_TO_CATCH_A_SEAT 회
        count_catch_a_seat = 0

        while 1:
            count_catch_a_seat = count_catch_a_seat + 1

            # uncheck seat
            time.sleep(self.TRY_TO_CATCH_INTERVAL)

            self.browser.switch_to.default_content()
            self.browser.execute_script("fnPrevStep()")
            time.sleep(1)

            self.browser.switch_to.default_content()
            self.browser.switch_to.frame('ifrmSeat')

            sty_select_seat_list = self.browser.find_elements_by_css_selector(
                'img.stySelectSeat')
            print(sty_select_seat_list[0].get_attribute('alt') + ' uncheck!')
            sty_select_seat_list[0].click()
            time.sleep(1)

            # 최대 RETRY 수를 넘으면 retry 종료 (루프 종료)
            if count_catch_a_seat > self.MAX_TRY_TO_CATCH_A_SEAT:
                print('RELEASE A SEAT')
                self.browser.switch_to.default_content()
                break

            # re-check seat
            sty_seat_list = self.browser.find_elements_by_css_selector('img.stySeat')
            if sty_seat_list.__len__() > 0:
                print(sty_seat_list[0].get_attribute('alt') + ' re-check!')
                sty_seat_list[0].click()

                time.sleep(1)
                self.browser.execute_script("fnSelect();")
                time.sleep(1)
                print('RE-CATCH A SEAT!!, RETRY COUNT = ' + str(count_catch_a_seat))
                self.browser.switch_to.default_content()
            else:
                # 중간에 자리를 뺏겨서 다시 잡을수 없으면, retry 종료 (루프 종료)
                print('CANNOT SELECT A SEAT.. T^T, RETRY COUNT = '
                      + str(count_catch_a_seat))
                self.browser.switch_to.default_content()
                break

        # Retry 초과 또는 중간에 자리 뺏기면, 팝업 종료 후 이전 윈도우로 복귀
        self.browser.execute_script("window.close()")
        self.browser.switch_to.window(self.window_name)
        return

    @staticmethod
    def __is_exclude(exclude_keyword_list, product_group_text):
        # 상품 그룹에서 exclude keyword 필터링 (카라반@폴딩)
        print("current product name : {}".format(product_group_text))
        for exclude_keyword in exclude_keyword_list:
            if product_group_text.find(exclude_keyword) > -1:
                print("this product is include the 'exclude keyword({})'.".format(exclude_keyword))
                return True
        return False
