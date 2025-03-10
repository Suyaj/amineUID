from selenium.webdriver.support import expected_conditions as ec

from selenium import webdriver
from PIL import Image
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait

# 设置代理IP
proxy_ip = "127.0.0.1"
proxy_port = "7890"
time_out = 60
js='''window.isAllImgLoaded = function(root,imgs){let espectImgs=imgs.split(",");let imgNodeList=root.querySelectorAll("img");let imgArr=Array.prototype.slice.call(imgNodeList);result={};for(let img of espectImgs){result[img]="0"}let resultKeys=Object.keys(result);for(let img of imgArr){if(!!!img.attributes["src"]){continue}if(resultKeys.indexOf(img.attributes["src"].value)==-1){continue}if(img.complete){result[img.attributes["src"].value]="1"}}return result}'''

# 设置代理
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = f"{proxy_ip}:{proxy_port}"
proxy.ssl_proxy = f"{proxy_ip}:{proxy_port}"

url = 'https://homdgcat.wiki/gi/char/Varesa#_Varesa'
option = webdriver.ChromeOptions()
option.add_argument('headless')
option.add_argument('--no-sandbox')
option.add_argument('--proxy-server=http://{}:{}'.format(proxy_ip, proxy_port))
driver = webdriver.Chrome(options=option)
# driver.implicitly_wait(10)
driver.get(url)

width = driver.execute_script("return document.documentElement.scrollWidth")
height = driver.execute_script("return document.documentElement.scrollHeight")
driver.set_window_size(width, height)  # 修改浏览器窗口大小
# 搜索结果部分完整截图
try:
    element = WebDriverWait(driver, time_out).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, '.gacha.dissolve'))
    )
    readyState = driver.execute_script(
        "return document.getElementById('special').getElementsByClassName('gacha dissolve')[0].complete;")
    while not readyState:
        readyState = driver.execute_script(
            "return document.getElementById('special').getElementsByClassName('gacha dissolve')[0].complete;")
    time.sleep(2)
    r_node = driver.find_element(By.CSS_SELECTOR, value='.a_data')
    print('网页模块尺寸:height={},width={}'.format(r_node.size['height'], r_node.size['width']))
    # driver.get_screenshot_as_file("bing_results.png")
    # 使用抠图的方式获得网页指定部分的截图
    r_node.screenshot('bing_results.png')  # 得到整个网页的完整截图
    im = Image.open('bing_results.png')
    print("截图尺寸:height={},width={}".format(im.size[1], im.size[0]))
    driver.close()
finally:
    driver.quit()
