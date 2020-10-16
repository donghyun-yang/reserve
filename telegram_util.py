import requests


class TelegramUtil:

    SEND_API_URL = "https://api.telegram.org/bot{token}/sendmessage?chat_id={chat_id}&text={message}"
    MAX_DUP_MSG_CNT = 30

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.prev_msg = ""
        self.dup_msg_cnt = 0

    def send_message(self, message):

        if self.prev_msg == message and self.dup_msg_cnt <= self.MAX_DUP_MSG_CNT:
            self.dup_msg_cnt += 1
            print("skip to send message, because previous massage is same to current message.")
            print("dup_msg_cnt : " + str(self.dup_msg_cnt))

        url = self.SEND_API_URL.format(token=self.token, chat_id=self.chat_id, message=message)
        resp = requests.get(url)
        print("resp : " + resp.text)
