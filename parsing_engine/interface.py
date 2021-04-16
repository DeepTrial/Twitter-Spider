#! /usr/bin/env python3

import csv
import datetime
import os
import pandas as pd
from time import sleep

from parsing_engine.driver import *
from parsing_engine.login.login_twitter import *
from parsing_engine.engine import open_user_page,open_search_page,get_page_tweets
from parsing_engine.media.image import download_images
from parsing_engine.media.video import download_videos
from parsing_engine.log import get_logger




def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
        return False
    else:
        return True

def login_website(driver,logger):
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

def load_history(filename,logger):
    history_set=set()
    df_file=open(filename,'r',encoding='utf-8-sig')
    history_df=pd.read_csv(df_file)
    logger.info("Load history tweet...")
    try:
        for i in range(len(history_df)):
            tweet_id = ''.join(history_df.iloc[i,0:3])+ history_df.iloc[i,-1]
            history_set.add(tweet_id)
    except:
        df_file.close()
        logger.exception("Load history tweet failed!")
    return history_set

def scrap_main_page(account,save_dir,headless=False,page_info="main",login=False,resume=False,proxy=None,save_image=False,save_video=False):

    logger=get_logger()
    driver = init_driver(headless, proxy, show_images=save_image)
    if login:
        driver=login_website(driver,logger)

    current_date=datetime.date.today().isoformat()
    csv_logfile_name=os.path.join(save_dir,account+".csv")
    check_dir(save_dir)

    tweet_ids=set()
    write_mode="w"
    if resume:
        tweet_ids=load_history(csv_logfile_name,logger)
        write_mode="a"
    data=[]
    with open(csv_logfile_name,write_mode,newline='',encoding='utf-8-sig') as f:
        header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes', 'Retweets','Image link', 'Video link', 'Tweet URL']
        writer = csv.writer(f)
        if not resume:
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


def scrap_between_date(account,start_date,end_date,save_dir,headless=False,login=False,proxy=None,save_image=False,save_video=False,lang=None):

    logger = get_logger()
    driver = init_driver(headless, proxy, show_images=save_image)

    if login:
        driver = login_website(driver, logger)

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

        max_date_str=end_date.__format__('%Y-%m-%d')
        start_date_str=start_date.__format__('%Y-%m-%d')
        open_search_page(driver, account, None, start_date_str, max_date_str, lang=lang)
        sleep(5)
        keep_scrolling = True
        while keep_scrolling:
            current_position = get_current_Y_offset(driver)
            driver, data, writer, tweet_ids= get_page_tweets(driver,account, data, writer, tweet_ids,logger)
            driver = driver_scroling(driver, 700)
            if get_current_Y_offset(driver) == current_position:
                keep_scrolling = False


    data = pd.DataFrame(data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes','Retweets', 'Image link', 'Video link', 'Tweet URL'])

    # save_images
    if save_image:
        download_images(data, save_dir,logger)

    # save_videos
    if save_video:
        download_videos(data, save_dir,logger)

    driver.close()