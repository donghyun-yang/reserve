#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from reserve.macro.xticket_macro.xticket_macro import XTicketMacro

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://camp.xticket.kr/web/main?shopEncode=3ca13d7e35f571dd445d29950216553a5ece8a50aa56784c7a287e2f4f438131"
NAME = "중랑캠핑장"


def main():
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "" or not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "":
        raise Exception("Should be set telegram TOKEN and CHAT_ID")
    else:
        print("TELEGRAM TOKEN : " + TELEGRAM_TOKEN)
        print("TELEGRAM CHAT_ID : " + TELEGRAM_CHAT_ID)

    url = URL
    XTicketMacro(NAME, url, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID).process()


if __name__ == '__main__':
    main()

