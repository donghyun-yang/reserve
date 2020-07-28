#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
import time, sys
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui  import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Queue

mobile_emulation = {
    "deviceMetrics": {"width": 360, "height": 900, "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 BUILD/JOP400) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
}

chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

browser = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
browser.set_window_size(400, 940)

TARGET_DAY = 4  # sun : 0, sat: 6
MAX_MONTH_CNT = 2  # 몇 개월치에 대해 확인 할 것인지


class XTicketMacro:

    def move_to_next_month(self, idx):
        if idx == 0:
            reversed_idx = 1
        else:
            reversed_idx = 0

        from_element = browser.find_elements_by_css_selector('div#calendarWrap.rollPanel div table.calendarList')[
            reversed_idx].find_elements_by_css_selector('tbody tr td')[4]
        to_element = browser.find_elements_by_css_selector('div#calendarWrap.rollPanel div table.calendarList')[
            reversed_idx].find_elements_by_css_selector('tbody tr td')[2]
        ActionChains(browser).drag_and_drop(from_element, to_element).perform()
        print('move to next month')
        time.sleep(3)

    def close_notices(self):
        browser.execute_script(
            "const buttonList = $('div.modalCntLayer div.wrapNoticeLayer div.wrapBtnBottom button.btnTy1.btnCancel'); for (var i=buttonList.length-1; i>=0; i--) { buttonList[i].click() }")  # mobile

    def __load_tr_list(self, idx_calendar_list) -> list:
        self.tr_list: list = browser.find_elements_by_css_selector('div#calendarWrap.rollPanel div table.calendarList')[
            idx_calendar_list].find_elements_by_css_selector('tbody tr')

    def check_bookable(self, idx_calendar_list):
        try:
            self.__load_tr_list(idx_calendar_list)

            for number_of_week in range(0, self.tr_list.__len__()):
                tr = self.tr_list[number_of_week]
                number_of_week = number_of_week + 1
                try:
                    td_list = tr.find_elements_by_css_selector('td')
                except exceptions.StaleElementReferenceException:
                    self.__load_tr_list(idx_calendar_list)
                    tr = self.tr_list[number_of_week - 1]
                    td_list = tr.find_elements_by_css_selector('td')

                current_date = td_list[TARGET_DAY]
                current_date_text = td_list[TARGET_DAY].get_property('innerHTML')
                if current_date_text == '':
                    if number_of_week == 1:
                        print(str(number_of_week) + '번째 주차에' + str(TARGET_DAY) + '번째 요일이 없음!')
                    else:
                        print('해당 월 ' + str(number_of_week) + '번째 주차까지 모든 주 탐색 완료, 다음월로 이동될 거 임')
                        break
                else:
                    if current_date.get_attribute('class').find('bookable') != -1:
                        print(current_date_text + '일 click')
                        # XPATH에서 index는 0부터가 아니고 1부터임
                        # 잘 안됨... 그냥 move to next month 후 time.sleep(3)이 잘됨
                        # WebDriverWait(browser, 10).until(EC.element_to_be_clickable(By.XPATH, "//div[@id='calendarWrap']/div/table[@class='calendarList'][" + str(idx_calendar_list+1) + "]/tbody/tr[" + str(cnt) + "]/td[" + str(TARGET_DAY+1) + "]"))

                        current_date.click()
                        time.sleep(1)

                        product_group_list = browser.find_elements_by_css_selector('ul.productGroupList li')
                        for product_group in product_group_list:
                            product_group_text = product_group.get_property('innerHTML')
                            product_group.click()
                            time.sleep(1)

                            bookable_list = browser.find_elements_by_css_selector('ul#listShow li')
                            time.sleep(1)

                            if bookable_list.__len__() > 0:
                                for bookable in bookable_list:
                                    print(bookable.text)
                                    print(current_date_text + '일 ' + product_group_text + ' 예약가능!!!')
                            else:
                                print(current_date_text + '일 ' + product_group_text + ' 매진')
                    else:
                        print(current_date_text + '일은 예약이 불가능한 날짜')
                        time.sleep(1)
        except exceptions.StaleElementReferenceException as e:
            raise e
        except Exception as e:
            print('Unexpected error:', sys.exc_info())
            print('Exception:', e)
            return False

        return True


def main():
    while 1:
        browser.get(
            "https://camp.xticket.kr/web/main?shopEncode=3ca13d7e35f571dd445d29950216553a5ece8a50aa56784c7a287e2f4f438131")
        time.sleep(5)

        # 악성코드 차단 링크에서 !회성 사용 베너 클릭
        print(browser.current_url)
        if browser.current_url.find('notify-HTTPS_Notice') != -1:
            browser.find_element_by_css_selector('html body table tbody tr td div a').click()
            time.sleep(5)

        xticket_macro = XTicketMacro()

        # 공지사항 닫기
        xticket_macro.close_notices()

        # List로 보기
        browser.find_element_by_css_selector('h3.listShow a').click()
        time.sleep(5)

        month_cnt = 0

        for i in range(0, MAX_MONTH_CNT):
            idx_calendar_list = (month_cnt + 2) % 2

            if month_cnt > 0:
                xticket_macro.move_to_next_month(idx_calendar_list)

            month_cnt = month_cnt + 1

            if not xticket_macro.check_bookable(idx_calendar_list):
                print('월 탐색 비정상 종료')
                break
            else:
                print('월 탐색 정상 종료')

        print('==================== 모든 대상 월 탐색 완료 ===================')


main()
browser.quit()
