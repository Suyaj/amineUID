import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

if __name__ == '__main__':
    option = webdriver.FirefoxOptions()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-gpu')
    option.add_argument('--disable-dev-shadow')
    option.add_argument('--allow-system-access')
    service = Service(executable_path='/snap/bin/geckodriver')
    driver = webdriver.Firefox(options=option, service=service)
    try:
        driver.get("https://homdgcat.wiki")
        WebDriverWait(driver, 60).until(
            ec.presence_of_element_located((By.XPATH, '/html/body/container/div/section[4]'))
        )
        ready_state = driver.execute_script(
            "let images = document.getElementsByClassName('n1')[0].getElementsByTagName('img');for (let image of images) {  if(!image.complete){    return false;  }}return true;")
        while not ready_state:
            ready_state = driver.execute_script(
                "let images = document.getElementsByClassName('n1')[0].getElementsByTagName('img');for (let image of images) {  if(!image.complete){    return false;  }}return true;")
        time.sleep(1)
        html = driver.find_element(By.CSS_SELECTOR, 'container')
        # 将浏览器的宽高设置最大
        driver.set_window_size(html.size['width'], html.size['height'])
        time.sleep(1)
        r_node = driver.find_element(By.XPATH, value='/html/body/container/div/section[4]')
    except Exception as e:
        print('请求错误:{}', e)
    finally:
        driver.quit()
