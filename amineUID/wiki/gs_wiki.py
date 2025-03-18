import asyncio
import platform
from pathlib import Path

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from amineUID.utils.contants import WIKI_URL, FUTURE_PATH
from gsuid_core.bot import Bot
from gsuid_core.logger import logger

import time
import uuid
import base64

time_out = 60
host = WIKI_URL
executable_path = '/snap/bin/geckodriver'
gs_future = Path.joinpath(FUTURE_PATH, 'gs_future')
sr_future = Path.joinpath(FUTURE_PATH, 'sr_future')
data_future = Path.joinpath(FUTURE_PATH, 'data')


async def refresh_data(bot: Bot = None):
    page_source = await get_future()
    html = BeautifulSoup(page_source, 'html.parser')
    target_list = get_text(html)
    text_list = target_list['gs']
    # await get_gs_node_images(html, text_list)
    text_list = target_list['sr']
    await get_sr_node_images(html, text_list)


async def get_gs_node_images(html, text_list):
    for text in text_list:
        target = get_url_target(html, text)
        await gs_screen_shot(target, text)


async def get_sr_node_images(html, text_list):
    for text in text_list:
        target = get_url_target(html, text)
        await sr_screen_shot(target, text)


async def sr_screen_shot(url: str, name: str):
    request_url = host + url
    driver = get_driver()
    if driver is None:
        return
    # 搜索结果部分完整截图
    try:
        driver.get(request_url)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="content_2"]/div'))
        )
        driver.execute_script("document.body.style.zoom='0.1'")
        time.sleep(0.5)
        await wait(driver, "mon_body")
        time.sleep(0.5)
        driver.execute_script("document.body.style.zoom='1'")
        time.sleep(1)
        html = driver.find_element(By.CSS_SELECTOR, 'container')
        # 将浏览器的宽高设置最大
        driver.set_window_size(html.size['width'], html.size['height'] + 200)
        time.sleep(0.5)
        node = driver.find_element(By.XPATH, value="//*[@id='content_2']/div")
        if data_future.exists() is False:
            data_future.mkdir()
        node.screenshot(str(Path.joinpath(data_future, f'{name}.png')).rstrip("\\"))  # 得到整个网页的完整截图
    except Exception as e:
        logger.error('请求错误:{}', e)
    finally:
        driver.quit()


def get_sr_type(driver):
    elements = driver.find_elements(By.CLASS_NAME, value="a_section")
    length = len(elements)
    if length == 18:
        return 1
    else:
        exist = is_exist(driver, 't_skill')
        if exist:
            return 2
        else:
            return 3


async def gs_screen_shot(url: str, name: str):
    request_url = host + url
    driver = get_driver()
    if driver is None:
        return
    # 搜索结果部分完整截图
    try:
        driver.get(request_url)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.XPATH, '/html'))
        )
        _type = get_gs_type(driver)
        driver.execute_script("document.body.style.zoom='0.1'")
        if _type == 1:
            await wait(driver, "a_data")
        elif _type == 2:
            await wait(driver, "r_data")
        else:
            await wait(driver, "weapon_section")
        time.sleep(0.5)
        driver.execute_script("document.body.style.zoom='1'")
        time.sleep(1)
        html = driver.find_element(By.CSS_SELECTOR, 'container')
        # 将浏览器的宽高设置最大
        driver.set_window_size(html.size['width'], html.size['height'] + 200)
        time.sleep(0.5)
        if _type == 1:
            node = driver.find_element(By.XPATH, value="/html/body/div[1]/container/divv/section[4]")
        elif _type == 2:
            node = driver.find_element(By.XPATH, value="/html/body/div[1]/container/divv/section[3]/div[1]")
        else:
            node = driver.find_element(By.XPATH, value="/html/body/div[1]/container/divv/section[3]")
        if data_future.exists() is False:
            data_future.mkdir()
        node.screenshot(str(Path.joinpath(data_future, f'{name}.png')).rstrip("\\"))  # 得到整个网页的完整截图
    except Exception as e:
        logger.error('请求错误:{}', e)
    finally:
        driver.quit()


def get_gs_type(driver):
    _bool = is_exist(driver, 'a_data')
    if _bool:
        return 1
    else:
        _bool = is_exist(driver, 'r_data')
        if _bool:
            return 2
        else:
            return 3


def is_exist(driver, class_name):
    try:
        driver.find_element(By.CLASS_NAME, class_name)
        return True
    except NoSuchElementException:
        return False


async def get_future():
    request_url = host
    driver = get_driver()
    if driver is None:
        return
    # 搜索结果部分完整截图
    try:
        driver.get(request_url)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.XPATH, '/html/body/container/div/section[4]'))
        )
        await wait(driver, "n1")
        time.sleep(0.5)
        html = driver.find_element(By.CSS_SELECTOR, 'container')
        # 将浏览器的宽高设置最大
        driver.set_window_size(html.size['width'], html.size['height'])
        time.sleep(0.5)
        r_node = driver.find_element(By.XPATH, value='/html/body/container/div/section[4]')
        await to_future_image(r_node, gs_future)
        driver.find_element(By.XPATH, '/html/body/container/div/section[1]/schedule[2]').click()
        await wait(driver, "n2")
        time.sleep(0.5)
        r_node = driver.find_element(By.XPATH, value='/html/body/container/div/section[5]')
        await to_future_image(r_node, sr_future)
        # 返回页面数据
        return driver.page_source
    except Exception as e:
        logger.error('请求错误:{}', e)
    finally:
        driver.quit()


async def wait(driver, class_name: str):
    execute_script = "let images = document.getElementsByClassName('" + class_name + "')[0].getElementsByTagName('img');for (let image of images) {  if(!image.complete){    return false;  }}return true;"
    ready_state = driver.execute_script(execute_script)
    while not ready_state:
        ready_state = driver.execute_script(execute_script)


async def to_future_image(r_node, path: str):
    _base64 = r_node.screenshot_as_base64
    elements = r_node.find_elements(By.CSS_SELECTOR, 'a')
    size = len(elements)
    _width = elements[0].size['width']
    img_width = (_width + 8) * size
    binary_data = base64.b64decode(_base64)
    image_data = BytesIO(binary_data)
    img = Image.open(image_data)
    height = img.size[1] - 16
    im = img.crop((0, 0, img_width, height))
    if FUTURE_PATH.exists() is False:
        FUTURE_PATH.mkdir()
    im.save(f'{path}.png')


def get_temp_file():
    image_id = uuid.uuid4()
    path = image_id.__str__() + '.png'
    return path


def get_driver():
    try:
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-gpu')
        option.add_argument('--disable-dev-shadow')
        option.add_argument('--allow-system-access')
        os_name = platform.system()
        if os_name.lower() == 'windows':
            service = Service(executable_path=None)
        else:
            service = Service(executable_path=executable_path)
        driver = webdriver.Chrome(options=option, service=service)
        driver.implicitly_wait(20)
        driver.maximize_window()
        return driver
    except Exception as e:
        logger.error(f"webdriver启动失败：{e}")


def get_text(html: BeautifulSoup):
    gs = html.find("section", {"class": "n1"})
    gs_text_list = get_text_list(gs)
    sr = html.find("section", {"class": "n2"})
    sr_text_list = get_text_list(sr)
    return {"gs": gs_text_list, "sr": sr_text_list}


def get_html(_url: str):
    driver = get_driver()
    if driver is None:
        return
    try:
        driver.get(_url)
        time.sleep(1)
        WebDriverWait(driver, time_out).until(
            ec.presence_of_element_located((By.XPATH, '/html'))
        )
        time.sleep(1)
        page_source = driver.page_source
        html = BeautifulSoup(page_source, 'html.parser')
        return html
    finally:
        driver.quit()


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


# url = get_url("瓦雷莎")
# print(url)
if __name__ == '__main__':
    asyncio.run(refresh_data())
    # asyncio.run(screen_shot('/gi/char/Varesa',  "test"))
