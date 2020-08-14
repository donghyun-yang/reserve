import os

from interpark_macro import InterparkMacro

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def main():
    url = "http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?GoodsCode=20003498"
    interpark_macro = InterparkMacro(url, camp_name="공릉캠핑장", is_catch_a_seat=False,
                                     telegram_token=TELEGRAM_TOKEN, telegram_chat_id=TELEGRAM_CHAT_ID,
                                     target_day="sat", product_group_keyword="ALL")

    # interpark_macro.TRY_TO_CATCH_INTERVAL = 3
    # interpark_macro.MAX_TRY_TO_CATCH_A_SEAT = 1
    interpark_macro.run()


if __name__ == '__main__':
    main()
