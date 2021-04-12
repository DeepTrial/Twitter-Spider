
import time
from selenium.webdriver.support.wait import WebDriverWait
import parsing_engine.login.username_password as const
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
from selenium.webdriver.common.by import By
from time import sleep
import os

#login twitter with password
def login_pwd(driver,logger):

    driver.get('https://www.twitter.com/login')
    # 输入账号密码
    sleep(15)
    username = const.USERNAME
    password = const.PASSWORD
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
    time.sleep(3)
    # 生成登录后快照
    # 保存当前登录的cookie
    dictCookies = driver.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    # 登录完成后，将cookie保存到本地文件
    with open('./cookies.json', 'w') as f:
        f.write(jsonCookies)

    logger.warning('Login with password Successful！Next time will try to login with cookie')
    return driver


#login twitter with cookies
def login_cookie(driver,logger):
    logger.info("try to login with cookie...")
    if os.path.exists('./cookies.json'):
        pass
    else:
        logger.warning("cookies not found")
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
    logger.info('login with cookie success!')
    return driver
