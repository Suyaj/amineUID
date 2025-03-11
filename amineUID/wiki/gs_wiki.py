from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from PIL import Image

import time
import requests

# 设置代理IP
proxy_ip = "127.0.0.1"
proxy_port = "7890"
time_out = 60
host = 'https://homdgcat.wiki'


def screen_shot(url: str, div_id: str, element: str):
    # 设置代理
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = f"{proxy_ip}:{proxy_port}"
    proxy.ssl_proxy = f"{proxy_ip}:{proxy_port}"

    url = host + url
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-gpu')
    option.add_argument('--proxy-server=http://{}:{}'.format(proxy_ip, proxy_port))
    driver = webdriver.Chrome(options=option)
    driver.implicitly_wait(20)
    driver.maximize_window()
    # 搜索结果部分完整截图
    try:
        driver.get(url)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, '.gacha.dissolve'))
        )
        ready_state = driver.execute_script(
            "return document.getElementById('{}').getElementsByClassName('{}')[0].complete;".format(div_id, element))
        while not ready_state:
            ready_state = driver.execute_script(
                "return document.getElementById('{}').getElementsByClassName('{}')[0].complete;"
                .format(div_id, element))
        time.sleep(1)
        r_node = driver.find_element(By.CSS_SELECTOR, value='.a_data')
        print('网页模块尺寸:height={},width={}'.format(r_node.size['height'], r_node.size['width']))
        # 将浏览器的宽高设置成刚刚获取的宽高
        driver.set_window_size(r_node.size['width'] + 100, r_node.size['height'] + 100)
        time.sleep(1)
        r_node = driver.find_element(By.CSS_SELECTOR, value='.a_data')
        r_node.screenshot('bing_results.png')  # 得到整个网页的完整截图
        im = Image.open('bing_results.png')
        print("截图尺寸:height={},width={}".format(im.size[1], im.size[0]))
        driver.close()
    except Exception as e:
        print('请求超时')
    finally:
        driver.quit()


screen_shot('/gi/char/Varesa#_Varesa', 'special', 'gacha dissolve')
