from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import base64
from io import BytesIO
from PIL import Image

STRUCTURE_DROPDOWN = (By.XPATH, "//nav/div/div[2]/ul/li[4]/a")
LOAD_MOL = (By.XPATH, "//nav/div/div[2]/ul/li[4]/ul/li[3]/a")
GET_IMAGE = (By.XPATH, "//nav/div/div[2]/ul/li[4]/ul/li[18]/a")
BUTTON_ACCEPT_INPUT = (By.ID, "btnAcceptInput")
BUTTON_CLOSE = (By.XPATH, "//div[@id='modalApiResult']/div/div/div[3]/button[2]")

INPUT_CONTENT = (By.ID, "modalApiInputContent")
OUTPUT_CONTENT = (By.ID, "modalApiResultContentText")

API_CALLS = (By.XPATH, "//nav/div/div[2]/ul[2]/li[2]/a/span")

MAX_ATTEMPTS = 10

class ChemDraw:
    def __init__(self) -> None:
        options = Options()
        options.add_argument("--headless")

        driver = webdriver.Firefox(options=options)

        driver.get("https://chemdrawdirect.perkinelmer.cloud/js/sample/index.html#")
        assert "ChemDraw JS Sample Page" in driver.title

        time.sleep(1.5)

        self.driver = driver
    
    def uploadmol(self, str):
        self.click(STRUCTURE_DROPDOWN)
        self.click(LOAD_MOL)
        self.find(INPUT_CONTENT).send_keys(str)
        self.click(BUTTON_ACCEPT_INPUT)

    def downloadimage(self, size):
        self.click(STRUCTURE_DROPDOWN)
        self.click(GET_IMAGE)
        time.sleep(0.3)
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            try:
                image = Image.open(BytesIO(base64.b64decode(self.find(OUTPUT_CONTENT).text[22:-1] + "=="))).resize(size)
                break
            except Exception:
                time.sleep(0.3)
                attempts += 1
        if attempts == MAX_ATTEMPTS:
            raise Exception("Image Processing Error")

        self.click(BUTTON_CLOSE)
        return image
    
    def getapicalls(self):
        return int(self.find(API_CALLS).text)

    def reset(self):
        self.quit()
        self.__init__()

    def quit(self):
        self.driver.quit()

    def find(self, element):
        return self.driver.find_element(element[0], element[1])

    def click(self, element):
        element = self.driver.find_element(element[0], element[1])
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            try:
                element.click()
                break
            except ElementClickInterceptedException:
                time.sleep(0.3)
                attempts += 1
        if attempts == MAX_ATTEMPTS:
            raise ElementClickInterceptedException
