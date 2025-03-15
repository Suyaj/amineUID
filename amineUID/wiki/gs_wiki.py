from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from gsuid_core.logger import logger

import time
import uuid
import base64

# 设置代理IP
proxy_ip = "127.0.0.1"
proxy_port = "7890"
time_out = 60
host = 'https://homdgcat.wiki'
# 设置代理
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = f"{proxy_ip}:{proxy_port}"
proxy.ssl_proxy = f"{proxy_ip}:{proxy_port}"
driver_path = ''

def screen_shot(url: str, div_id: str | None, element: str | None, wait_xpath: str, script_state: str | None,
                node_xpath: str):
    request_url = host + url
    driver = get_driver()
    # 搜索结果部分完整截图
    try:
        driver.get(request_url)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.XPATH, wait_xpath))
        )
        if script_state is not None:
            ready_state = driver.execute_script(script_state)
        else:
            ready_state = driver.execute_script(
                "return document.getElementById('{}').getElementsByClassName('{}')[0].complete;"
                .format(div_id, element))
        while not ready_state:
            if script_state is not None:
                ready_state = driver.execute_script(script_state)
            else:
                ready_state = driver.execute_script(
                    "return document.getElementById('{}').getElementsByClassName('{}')[0].complete;"
                    .format(div_id, element))
        time.sleep(1)
        html = driver.find_element(By.CSS_SELECTOR, 'container')
        # 将浏览器的宽高设置最大
        driver.set_window_size(html.size['width'], html.size['height'])
        time.sleep(1)
        r_node = driver.find_element(By.XPATH, value=node_xpath)
        r_node.screenshot('bing_results.png')  # 得到整个网页的完整截图
        return r_node.screenshot_as_base64, r_node.find_elements(By.CSS_SELECTOR, 'a')
    except Exception as e:
        logger.error('请求错误:{}', e)
    finally:
        driver.close()


def get_future(_type: str):
    if _type == 'gs':
        r_node_target = '/html/body/container/div/section[4]'
    else:
        r_node_target = '/html/body/container/div/section[5]'
    request_url = host
    driver = get_driver()
    # 搜索结果部分完整截图
    try:
        driver.get(request_url)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.XPATH, '/html/body/container/div/section[4]'))
        )
        ready_state = driver.execute_script(
            "let images = document.getElementsByClassName('n1')[0].getElementsByTagName('img');for (let image of images) {  if(!image.complete){    return false;  }}return true;")
        while not ready_state:
            ready_state = driver.execute_script(
                "let images = document.getElementsByClassName('n1')[0].getElementsByTagName('img');for (let image of images) {  if(!image.complete){    return false;  }}return true;")
        time.sleep(1)
        if _type != 'gs':
            driver.find_element(By.XPATH, '/html/body/container/div/section[1]/schedule[2]').click()
        html = driver.find_element(By.CSS_SELECTOR, 'container')
        # 将浏览器的宽高设置最大
        driver.set_window_size(html.size['width'], html.size['height'])
        time.sleep(1)
        r_node = driver.find_element(By.XPATH, value=r_node_target)
        _base64 = r_node.screenshot_as_base64
        elements = r_node.find_elements(By.CSS_SELECTOR, 'a')
        size = len(elements)
        _width = elements[0].size['width']
        img_width = (_width + 8) * size
        binary_data = base64.b64decode(_base64)
        image_data = BytesIO(binary_data)
        img = Image.open(image_data)
        height = img.size[1]
        im = img.crop((0, 0, img_width, height))
        return im
    except Exception as e:
        logger.error('请求错误:{}', e)
    finally:
        driver.close()


def get_temp_file():
    image_id = uuid.uuid4()
    path = image_id.__str__() + '.png'
    return path


def get_driver():
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-gpu')
    option.add_argument('--proxy-server=http://{}:{}'.format(proxy_ip, proxy_port))
    service = Service(driver_path=driver_path, options=option)
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(20)
    driver.maximize_window()
    return driver


def get_text():
    html = get_html(host)
    gs = html.find("section", {"class": "n1"})
    gs_text_list = get_text_list(gs)
    sr = html.find("section", {"class": "n2"})
    sr_text_list = get_text_list(sr)
    return {"原神": gs_text_list, "崩铁": sr_text_list}


def get_url(target: str):
    html = get_html(host)
    return get_url_target(html, target)


def get_html(_url: str):
    driver = get_driver()
    driver.get(_url)
    time.sleep(1)
    WebDriverWait(driver, time_out).until(
        ec.presence_of_element_located((By.XPATH, '/html'))
    )
    time.sleep(1)
    page_source = driver.page_source
    html = BeautifulSoup(page_source, 'html.parser')
    return html


def get_text_list(html):
    a_list = html.find_all("a", {"target": "_blank"})
    text_list = []
    for a in a_list:
        p = a.find_next("p", {"class": "new_text"})
        text_list.append(p.get_text())
    return text_list


def get_url_target(html, target):
    a_list = html.find_all("a", {"target": "_blank"})
    for a in a_list:
        p = a.find_next("p", {"class": "new_text"})
        if p.get_text() == target:
            return a['href']


# screen_shot('/gi/char/Varesa', 'special', 'gacha dissolve', '//*[@id="special"]', None,
#             '/html/body/div[1]/container/divv/section[4]')
# url = get_url("瓦雷莎")
# print(url)
future = get_future('sr')
print(future)
