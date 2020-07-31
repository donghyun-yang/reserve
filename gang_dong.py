#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xticket_macro import XTicketMacro


def main():
    url = "https://camp.xticket.kr/web/main?shopEncode=5f9422e223671b122a7f2c94f4e15c6f71cd1a49141314cf19adccb98162b5b0"
    XTicketMacro(url).run()


if __name__ == '__main__':
    main()

