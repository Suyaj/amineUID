from selenium import webdriver
from selenium.webdriver.firefox.service import Service


if __name__ == '__main__':
    option = webdriver.FirefoxOptions()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-gpu')
    option.add_argument('--disable-dev-shadow')
    option.add_argument('--allow-system-access')
    service = Service(port=4444, host='127.0.0.1')
    driver = webdriver.Firefox(options=option, service=service)
    try:
        driver.implicitly_wait(20)
    except Exception as e:
        print(f"webdriver启动失败：{e}")
    finally:
        driver.quit()

