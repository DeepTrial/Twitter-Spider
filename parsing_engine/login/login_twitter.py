#! /usr/bin/env python3

import json
import os
import parsing_engine.login.username_password as login_info
from parsing_engine.driver import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep


#login twitter with password
def login_pwd(driver,first=False):
    if first:
        driver = init_driver(False, None, show_images=False)
    driver.get('https://www.twitter.com/login')
    # 输入账号密码
    sleep(15)
    username = login_info.USERNAME
    password = login_info.PASSWORD
    #print(username,password)
    driver.get('https://www.twitter.com/login')
    username_xpath = '//input[@name="session[username_or_email]"]'
    password_xpath = '//input[@name="session[password]"]'

    username_el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, username_xpath)))
    password_el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, password_xpath)))

    username_el.send_keys(username)
    password_el.send_keys(password)
    password_el.send_keys(Keys.RETURN)
    # 等待3秒
    sleep(3)
    # 生成登录后快照
    # 保存当前登录的cookie
    dictCookies = driver.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    # 登录完成后，将cookie保存到本地文件
    with open('./cookies.json', 'w') as f:
        f.write(jsonCookies)

    print('Login with password Successful！Next time will try to login with cookie')
    if first:
        print("check whether there is a robot check")
        sleep(60)
    return driver


#login twitter with cookies
def login_cookie(driver):
    print("try to login with cookie...")
    if os.path.exists('./cookies.json'):
        pass
    else:
        print("cookies not found")
        raise FileNotFoundError
    with open('./cookies.json', 'r', encoding='utf-8') as f:
        listCookies = json.loads(f.read())
    driver.get('https://www.twitter.com/login')
    for cookie in listCookies:
        driver.add_cookie({
            'domain': cookie['domain'],
            'name': cookie['name'],
            'value': cookie['value'],
            'path': '/',
            'expires': None
        })
    # 再次访问页面，便可实现免登陆访问
    sleep(5)
    print('login with cookie success!')
    return driver
