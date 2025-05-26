import requests
import yaml

from gsuid_core.plugins.amineUID.amineUID.utils.contants import BOT_PATH


class HttpClient:
    def __init__(self):
        with open(BOT_PATH, "r", encoding="utf8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            bot = data['bot']
            self.host = bot['host']
            self.port = bot['port']
            self.password = bot['password']
            self.user_id = bot['userId']
            self.user_name = bot['userName']

            self.sp_msg = '/send_private_forward_msg'

    def send_private_msg(self, user_id: str, msgs: list[str]):
        message_list = []
        news = []
        for msg in msgs:
            message_list.append({'type': 'node', 'data': {
                "user_id": self.user_id,
                "nickname": self.user_name,
                "content": [
                    {
                        "type": "text",
                        "data": {
                            "text": msg
                        }
                    }
                ]
            }})
            news.append({
                'text': msg
            })

        raw = {"user_id": user_id, "message": message_list, 'source': self.user_name, 'news': news}
        headers = {'Authorization': f'Bearer {self.password}'}
        return self.__request(self.sp_msg, headers, raw)

    def __request(self, url, head, raw):
        _url = f'http://{self.host}:{self.port}{url}'
        return requests.post(_url, headers=head, json=raw)
