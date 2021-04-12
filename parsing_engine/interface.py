from parsing_engine.driver import *
from parsing_engine.login.login_twitter import *
from parsing_engine.engine import open_user_page,open_search_page,get_page_tweets
from parsing_engine.media.image import download_images
from parsing_engine.media.video import download_videos
from parsing_engine.log import get_logger
from time import sleep
import os
import datetime
import csv
import pandas as pd




def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
        return False
    else:
        return True

def login(driver,logger):
    try:
        logger.info('Login twitter with cookies')
        login_cookie(driver,logger)
    except:
        logger.warning('Login twitter with cookies failed. Try to login with pwd')
        try:
            sleep(3)
            login_pwd(driver,logger)
        except:
            logger.exception("Login failed. Please check with headless=False.")
            exit()
    return driver



def scrap_main_page(account,save_dir,headless=True,page_info="main",proxy=None,save_image=True,save_video=True):

    logger=get_logger()
    driver = init_driver(headless, proxy, show_images=save_image)
    driver=login(driver,logger)

    current_date=datetime.date.today().isoformat()
    csv_logfile_name=os.path.join(save_dir,account+"_"+current_date+".csv")
    check_dir(save_dir)

    tweet_ids=set()
    data=[]
    with open(csv_logfile_name,'w',newline='',encoding='utf-8-sig') as f:
        header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes', 'Retweets','Image link', 'Video link', 'Tweet URL']
        writer = csv.writer(f)
        writer.writerow(header)

        if page_info in ["main","with_replies","media","likes"]:
            open_user_page(driver,account,page_info)
        else:
            logger.exception("Page info error! Please check...")
            exit()
        keep_scrolling=True
        while keep_scrolling:
            current_position = get_current_Y_offset(driver)
            driver, data, writer, tweet_ids= get_page_tweets(driver, account,data, writer, tweet_ids,logger)
            driver=driver_scroling(driver, 900)
            if get_current_Y_offset(driver)==current_position:
                keep_scrolling=False
        sleep(2)
    data = pd.DataFrame(data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes','Retweets', 'Image link', 'Video link', 'Tweet URL'])

    # save_images
    if save_image:
        download_images(data, save_dir, logger)

    # save_videos
    if save_video:
        download_videos(data, save_dir, logger)

    driver.close()


def scrap_between_date(account,start_date,end_date,save_dir,interval=3,headless=True,proxy=None,save_image=True,save_video=True):

    logger = get_logger()
    driver = init_driver(headless, proxy, show_images=save_image)
    driver = login(driver, logger)

    start_date=datetime.date(int(start_date.split("-")[0]),int(start_date.split("-")[1]),int(start_date.split("-")[2]))
    end_date = datetime.date(int(end_date.split("-")[0]), int(end_date.split("-")[1]), int(end_date.split("-")[2]))

    start_date_str=start_date.__format__('%Y-%m-%d')
    end_date_str=end_date.__format__('%Y-%m-%d')

    csv_logfile_name = os.path.join(save_dir, account + "_" + start_date_str + "_"+end_date_str+".csv")
    check_dir(save_dir)

    tweet_ids = set()
    data = []
    with open(csv_logfile_name,'w',newline='',encoding='utf-8-sig') as f:
        header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes', 'Retweets','Image link', 'Video link', 'Tweet URL']
        writer = csv.writer(f)
        writer.writerow(header)

        while start_date <= end_date:

            max_date=start_date + datetime.timedelta(days=interval)
            max_date_str=max_date.__format__('%Y-%m-%d')
            start_date_str=start_date.__format__('%Y-%m-%d')
            open_search_page(driver, account, None, start_date_str, max_date_str)
            sleep(5)
            keep_scrolling = True
            while keep_scrolling:
                current_position = get_current_Y_offset(driver)
                driver, data, writer, tweet_ids= get_page_tweets(driver,account, data, writer, tweet_ids,logger)
                driver = driver_scroling(driver, 700)
                if get_current_Y_offset(driver) == current_position:
                    keep_scrolling = False

            start_date=start_date + datetime.timedelta(days=interval)

    data = pd.DataFrame(data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes','Retweets', 'Image link', 'Video link', 'Tweet URL'])

    # save_images
    if save_image:
        download_images(data, save_dir,logger)

    # save_videos
    if save_video:
        download_videos(data, save_dir,logger)

    driver.close()