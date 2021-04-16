#! /usr/bin/env python3

import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver



def init_driver(headless=True, proxy=None, show_images=False):
    """ initiate a chromedriver instance """

    # create instance of web driver
    chromedriver_path = chromedriver_autoinstaller.install()
    options = Options()
    if headless is True:
        options.add_argument('--disable-gpu')
        options.headless = True
    else:
        options.headless = False
    options.add_argument('log-level=3')
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)
    if show_images == False:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options,executable_path=chromedriver_path)
    driver.set_page_load_timeout(100)
    return driver


def get_current_Y_offset(driver):
    return driver.execute_script("return window.pageYOffset;")

def driver_scroling(driver,scroling_length=500):
    driver.execute_script('window.scrollBy(0,'+str(scroling_length)+');')
    return driver