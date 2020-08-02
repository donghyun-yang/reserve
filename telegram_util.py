import requests


class TelegramUtil:

    SEND_API_URL = "https://api.telegram.org/bot{token}/sendmessage?chat_id={chat_id}&text={message}"

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message):
        url = self.SEND_API_URL.format(token=self.token, chat_id=self.chat_id, message=message)
        resp = requests.get(url)
        print("resp : " + resp.text)
