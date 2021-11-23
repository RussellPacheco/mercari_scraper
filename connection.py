from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DRIVER_PATH = os.path.join(ROOT_PATH, "driver/chromedriver.exe")

OPTIONS = Options()
OPTIONS.headless = True
OPTIONS.add_argument("--incognito")

driver = webdriver.Chrome(options=OPTIONS, executable_path=DRIVER_PATH)
driver.get("https://jp.mercari.com/search?keyword=nvidia%203060ti&page=1&status=on_sale")