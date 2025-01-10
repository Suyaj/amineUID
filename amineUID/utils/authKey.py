import time

import requests


def get_auth_key(cookie: str):
    timestamp = time.time()
    headers = {"Cookie": cookie}
    response = requests.get(f"https://webapi.account.mihoyo.com/Api/login_by_cookie?t=${timestamp}", headers=headers)
    json = response.json()

