from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

from bs4 import BeautifulSoup

from gsuid_core.logger import logger

import time

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


def screen_shot(url: str, div_id: str | None, element: str | None, script_state: str | None):
    request_url = host + url
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
        driver.get(request_url)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.XPATH, '/html'))
        )
        if script_state is not None:
            ready_state = driver.execute_script(script_state)
        else:
            ready_state = driver.execute_script(
                "return document.getElementById('{}').getElementsByClassName('{}')[0].complete;"
                .format(div_id, element))
        while not ready_state:
            if script_state is not None:
                ready_state = driver.execute_script(script_state);
            else:
                ready_state = driver.execute_script(
                    "return document.getElementById('{}').getElementsByClassName('{}')[0].complete;"
                    .format(div_id, element))
        time.sleep(1)
        r_node = driver.find_element(By.CSS_SELECTOR, value='.a_data')
        # 将浏览器的宽高设置成刚刚获取的宽高
        driver.set_window_size(r_node.size['width'] + 100, r_node.size['height'] + 100)
        time.sleep(1)
        r_node = driver.find_element(By.CSS_SELECTOR, value='.a_data')
        r_node.screenshot('bing_results.png')  # 得到整个网页的完整截图
        return r_node.screenshot_as_base64
    except Exception as e:
        logger.error('请求错误:{}', e)
    finally:
        driver.close()


def get_future():
    screen_shot(host, None, None, '')


def get_driver():
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-gpu')
    option.add_argument('--proxy-server=http://{}:{}'.format(proxy_ip, proxy_port))
    driver = webdriver.Chrome(options=option)
    return driver


def get_text():
    driver = get_driver()
    driver.get(host)
    time.sleep(1)
    WebDriverWait(driver, time_out).until(
        ec.presence_of_element_located((By.XPATH, '/html'))
    )
    time.sleep(1)
    page_source = driver.page_source
    html = BeautifulSoup(page_source, 'html.parser')
    gs = html.find("section", {"class": "n1"})
    gs_text_list = get_text_list(gs)
    sr = html.find("section", {"class": "n2"})
    sr_text_list = get_text_list(sr)
    return {"原神": gs_text_list, "崩铁": sr_text_list}


def get_text_list(html):
    a_list = html.find_all("a", {"target": "_blank"})
    text_list = []
    for a in a_list:
        p = a.find_next("p", {"class": "new_text"})
        text_list.append(p.get_text())
    return text_list


def get_url(html, target):
    a_list = html.find_all("a", {"target": "_blank"})
    for a in a_list:
        p = a.find_next("p", {"class": "new_text"})
        if p.get_text() == target:
            return a.get_attribute("href")


# screen_shot('/gi/char/Varesa', 'special', 'gacha dissolve')
url = get_text()
print(url)
