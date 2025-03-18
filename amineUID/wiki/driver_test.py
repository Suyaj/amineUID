from selenium import webdriver
from selenium.webdriver.common.service import Service
from webdriver_manager.firefox import GeckoDriverManager


def get_driver():
    try:
        option = webdriver.FirefoxOptions()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-gpu')
        option.add_argument('--disable-dev-shadow')
        option.add_argument('--allow-system-access')
        path = GeckoDriverManager().install()
        service = Service(port=9515, executable_path=path)
        driver = webdriver.Firefox(options=option, service=service)
        driver.implicitly_wait(20)
        return driver
    except Exception as e:
        print(f"webdriver启动失败：{e}")

if __name__ == '__main__':
    _driver = get_driver()

