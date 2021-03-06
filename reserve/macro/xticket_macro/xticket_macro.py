import sys
import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
from reserve.macro.reserve_macro import ReserveMacro
from reserve.util.telegram_util import TelegramUtil


class XTicketMacro(ReserveMacro):

    def __init__(self, camp_name: str, url: str, telegram_token: str, telegram_chat_id: str, target_day: int = 6,
                 max_month_cnt: int = 2):
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 900, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 BUILD/JOP400) AppleWebKit/535.19 (KHTML, "
                         "like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19 "
        }

        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        chrome_options.add_argument('--disable-gpu')

        super().__init__(url, camp_name, telegram_token, telegram_chat_id, chrome_options)
        self.target_day = target_day  # sun : 0, sat: 6
        self.max_month_cnt = max_month_cnt  # 몇 개월치에 대해 확인 할 것인지
        self.current_month_text: str = "N/A"

    def _run(self):
        self._open_browser()

        while 1:
            try:
                self.__go_to_url()

                # 공지사항 닫기
                self.__close_notices()

                # List로 보기
                self.browser.find_element_by_css_selector('h3.listShow a').click()
                time.sleep(5)

                month_cnt = 0

                for i in range(0, self.max_month_cnt):
                    idx_calendar_list = (month_cnt + 2) % 2

                    if month_cnt > 0:
                        self.__move_to_next_month(idx_calendar_list)

                    month_cnt = month_cnt + 1

                    if not self.__check_bookable(idx_calendar_list):
                        print('월 탐색 비정상 종료')
                        break
                    else:
                        print('월 탐색 정상 종료')

                print('==================== 모든 대상 월 탐색 완료 ===================')
            except Exception as e:
                error_message = "[{camp_name}] Error is occurred!\n" \
                                "Exception : {exception}\n" \
                                "sys.exec_info : {exc_info}".format(camp_name=self.camp_name, exception=str(e),
                                                                    exc_info=sys.exc_info())
                print(error_message)
                self.telegram_util.send_message(error_message)

    def _open_browser(self):
        super()._open_browser()
        self.browser.set_window_size(400, 940)

    def __go_to_url(self):
        self.browser.get(self.url)
        time.sleep(5)
        self.__pass_office_blocking()

    def __pass_office_blocking(self):
        # 악성코드 차단 링크에서 !회성 사용 베너 클릭
        print(self.browser.current_url)
        if self.browser.current_url.find('notify-HTTPS_Notice') != -1:
            self.browser.find_element_by_css_selector('html body table tbody tr td div a').click()
            time.sleep(5)

    def __move_to_next_month(self, idx):
        if idx == 0:
            reversed_idx = 1
        else:
            reversed_idx = 0

        from_element = self.browser.find_elements_by_css_selector('div#calendarWrap.rollPanel div table.calendarList')[
            reversed_idx].find_elements_by_css_selector('tbody tr td')[4]
        to_element = self.browser.find_elements_by_css_selector('div#calendarWrap.rollPanel div table.calendarList')[
            reversed_idx].find_elements_by_css_selector('tbody tr td')[2]
        ActionChains(self.browser).drag_and_drop(from_element, to_element).perform()
        print('move to next month')
        time.sleep(3)

    def __close_notices(self):
        self.browser.execute_script(
            "const buttonList = $('div.modalCntLayer div.wrapNoticeLayer div.wrapBtnBottom button.btnTy1.btnCancel'); "
            "for (var i=buttonList.length-1; i>=0; i--) { buttonList[i].click() }")  # mobile

    def __load_tr_list(self, idx_calendar_list):
        self.tr_list: list = self.browser.find_elements_by_css_selector(
            'div#calendarWrap.rollPanel div table.calendarList'
        )[idx_calendar_list].find_elements_by_css_selector('tbody tr')

    def __check_bookable(self, idx_calendar_list):
        try:
            self.__load_tr_list(idx_calendar_list)

            self.current_month_text = self.__get_current_month()
            print("현재 월 : " + self.current_month_text)

            for number_of_week in range(0, self.tr_list.__len__()):
                tr = self.tr_list[number_of_week]
                number_of_week = number_of_week + 1
                try:
                    td_list = tr.find_elements_by_css_selector('td')
                except exceptions.StaleElementReferenceException:
                    self.__load_tr_list(idx_calendar_list)
                    tr = self.tr_list[number_of_week - 1]
                    td_list = tr.find_elements_by_css_selector('td')

                current_date = td_list[self.target_day]
                current_date_text = td_list[self.target_day].get_property('innerHTML')
                if current_date_text == '':
                    if number_of_week == 1:
                        print(str(number_of_week) + '번째 주차에' + str(self.target_day) + '번째 요일이 없음!')
                    else:
                        print(self.current_month_text + str(number_of_week)
                              + '번째 주차까지 모든 주 탐색 완료, 다음월로 이동될 거 임')
                        break
                else:
                    if current_date.get_attribute('class').find('bookable') != -1:
                        print(current_date_text + '일 click')

                        current_date.click()
                        time.sleep(1)

                        product_group_list = self.browser.find_elements_by_css_selector('ul.productGroupList li')
                        for product_group in product_group_list:
                            product_group_text = product_group.get_property('innerHTML')
                            product_group.click()
                            time.sleep(1)

                            bookable_list = self.browser.find_elements_by_css_selector('ul#listShow li')
                            time.sleep(1)

                            if bookable_list.__len__() > 0:
                                for bookable in bookable_list:
                                    message = "=============\n" \
                                              "[{camp_name}] {current_month_text} {current_date_text} 일 - " \
                                              "{product_group_text} 예약가능!!!'\n" \
                                              "{url}'\n" \
                                              "-------------\n" \
                                              "{bookable}\n" \
                                              "=============\n" \
                                        .format(camp_name=self.camp_name,
                                                current_month_text=self.current_month_text,
                                                current_date_text=current_date_text,
                                                product_group_text=product_group_text,
                                                url=self.url,
                                                bookable=bookable.text)

                                    self.telegram_util.send_message(message=message)
                                    print(message)
                            else:
                                print(current_date_text + '일 ' + product_group_text + ' 매진')
                    else:
                        print(current_date_text + '일은 예약이 불가능한 날짜')
                        time.sleep(1)
        except exceptions.StaleElementReferenceException as e:
            raise e
        except Exception as e:
            raise e

        return True

    def __get_current_month(self) -> str:
        return \
            self.browser.find_element_by_css_selector("#selectStep > li.step1.on > div:nth-child(2) > h2 > span").text
