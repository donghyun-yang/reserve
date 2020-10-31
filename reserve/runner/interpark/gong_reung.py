import os

from reserve.macro.interpark_macro.interpark_macro import InterparkMacro

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def main():
    url = "http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?GoodsCode=20008285"
    interpark_macro = InterparkMacro(url, camp_name="공릉캠핑장", is_catch_a_seat=True,
                                     telegram_token=TELEGRAM_TOKEN, telegram_chat_id=TELEGRAM_CHAT_ID,
                                     target_day="sat", exclude_keyword="카라반|폴딩")

    # interpark_macro.TRY_TO_CATCH_INTERVAL = 3
    # interpark_macro.MAX_TRY_TO_CATCH_A_SEAT = 1
    interpark_macro.process()


if __name__ == '__main__':
    main()
