#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from xticket_macro import XTicketMacro


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://camp.xticket.kr/web/main?shopEncode=5f9422e223671b122a7f2c94f4e15c6f71cd1a49141314cf19adccb98162b5b0"
NAME = "강동그린웨이캠핑장"


def main():
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "" or not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "":
        raise Exception("Should be set telegram TOKEN and CHAT_ID")
    else:
        print("TELEGRAM TOKEN : " + TELEGRAM_TOKEN)
        print("TELEGRAM CHAT_ID : " + TELEGRAM_CHAT_ID)

    url = URL
    XTicketMacro(NAME, url, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID).run()


if __name__ == '__main__':
    main()

