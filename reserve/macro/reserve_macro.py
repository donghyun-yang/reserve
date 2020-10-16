import abc
import os
import sys
import traceback

from reserve.util.telegram_util import TelegramUtil

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


class ReserveMacro(metaclass=abc.ABCMeta):
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
    BASE_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.path.pardir, os.path.pardir))

    if CURRENT_PATH.find("lib") != -1:
        BASE_PATH = os.path.abspath(os.path.join(BASE_PATH, os.path.pardir))

    DRIVER_PATH = os.path.join(BASE_PATH, "driver", "chromedriver.exe")
    print("current path : {}".format(CURRENT_PATH))
    print("base path : {}".format(BASE_PATH))
    print("driver path {}: ".format(DRIVER_PATH))

    def __init__(self, url, camp_name, telegram_token, telegram_chat_id, chrome_options):
        self.url = url
        self.telegram_util = TelegramUtil(telegram_token, telegram_chat_id)

        self.telegram_chat_id = telegram_chat_id
        self.telegram_token = telegram_token
        self.window_name = None
        self.camp_name = camp_name
        self.chrome_options = chrome_options

    def process(self):
        try:
            self._run()
        except Exception as e:
            traceback.print_exc()
            print(str(e))

            error_message = "[{camp_name}] Error is occurred!\n" \
                            "Exception : {exception}\n" \
                            "sys.exec_info : {exc_info}".format(camp_name=self.camp_name, exception=str(e),
                                                                exc_info=sys.exc_info())
            print(error_message)
            self.telegram_util.send_message(error_message)
            self._close_browser()
            self.process()

    @abc.abstractmethod
    def _run(self):
        pass

    @abc.abstractmethod
    def _open_browser(self):
        self.browser: WebDriver = webdriver.Chrome(executable_path=self.DRIVER_PATH, options=self.chrome_options)
        self.window_name = self.browser.window_handles[0]
        print("window_name : " + self.window_name)

    def _close_browser(self):
        self.browser.quit()
