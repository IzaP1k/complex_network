import time
# import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
# import Action chains
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import json

def sleepRandomTime(base_time=5, low_time=0.1, high_time=1.2):
    extra_time = random.uniform(low_time, high_time)
    wait_time = base_time + extra_time

    time.sleep(wait_time)


def showSite(is_link, by=By.XPATH, buttom_name='//button[@class="btn secondary reject-all"]'):
    driver = webdriver.Edge()

    driver.get(is_link)
    sleepRandomTime()


    return driver

driver = showSite(r"https://scholar.google.com/scholar?hl=pl&as_sdt=0%2C5&q=bci+motor+imagery&oq=BCI+motion+ima")

def getInfoColumns(driver, by=By.XPATH, kind="a",type="id", numberid="qVva4BNs_VUJ"):
    Table = driver.find_elements(by, f"//{kind}[contains(@{type}, {numberid})]")
    data_table = []

    stopper = 100

    for value in Table:

        stopper -= 1
        data_table.append(value.text)
        print(value.text)

        if stopper == 0:
            break

getInfoColumns(driver)

