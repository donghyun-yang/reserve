#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xticket_macro import XTicketMacro


def main():
    url = "https://camp.xticket.kr/web/main?shopEncode=3ca13d7e35f571dd445d29950216553a5ece8a50aa56784c7a287e2f4f438131"
    XTicketMacro(url).run()


if __name__ == '__main__':
    main()

