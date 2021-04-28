#! /usr/bin/env python3

import csv
import datetime
import os
import pandas as pd
import random
from time import sleep

from parsing_engine.driver import *
from parsing_engine.login.login_twitter import *
from parsing_engine.engine import open_user_page,open_search_page,get_page_tweets,get_user_info
from parsing_engine.media.image import download_images
from parsing_engine.media.video import download_videos
from parsing_engine.log import get_logger




def check_dir(dir):
    '''
    check the dir is exist or not. if it does not exist, create the dir
    '''
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
            sleep(20)
            login_pwd(driver,logger)
        except:
            logger.exception("Login failed. Please check with headless=False.")
            #exit()
    return driver

def load_history(filename,logger):
    '''
    load history tweet which have saved in the csv file
    filename:  filename for saved csv file
    '''
    history_set=set()
    # df_file=open(filename,'r',encoding='utf-8-sig')
    # history_df=pd.read_csv(df_file)
    logger.info("Load history tweet...")
    try:
        df_file = open(filename, 'r', encoding='utf-8-sig')
        history_df = pd.read_csv(df_file)
        for i in range(len(history_df)):
            tweet_id = ''.join(history_df.iloc[i,2])+ history_df.iloc[i,1]    # used to distinguish different tweets
            history_set.add(tweet_id)
    except:
        logger.warning("Load history tweet failed!")
    return history_set

def scrap_main_page(account,save_dir,headless=False,page_info="main",login=False,resume=False,proxy=None,save_image=False,save_video=False,continues=False,last_driver=None):

    logger=get_logger()
    ##################   init the webdriver   ####################
    driver = None
    if continues and last_driver:    #use current driver
        driver = last_driver
    else:
        driver = init_driver(headless, proxy, show_images=save_image)   # init a new driver
        if login:   # login twitter
            driver = login_website(driver, logger)
    ##############################################################

    ##################   init the csv file    ####################
    csv_logfile_name=os.path.join(save_dir,account+".csv")  #filename
    check_dir(save_dir)   # check the dir
    tweet_ids = set()     # init the database of tweets
    write_mode = "w"
    if resume:    # continue to scrap new tweets according to last step
        history_tweet_ids = load_history(csv_logfile_name, logger)
        if history_tweet_ids==tweet_ids:
            resume=False
            logger.info("Account: "+account+" has no history file!")
        if resume:
            write_mode = "a"

    ##############################################################

    data=[]
    with open(csv_logfile_name,write_mode,newline='',encoding='utf-8-sig') as f:
        header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes', 'Retweets','Image link', 'Video link', 'Tweet URL']
        writer = csv.writer(f)
        if not resume:   #if not continue to the existed csvfile, write the header index to file
            writer.writerow(header)

        if page_info in ["main","with_replies","media","likes"]:  #check if the page_info is in this 4 possible choice
            open_user_page(driver,account,page_info)   # open the selected page
            sleep(5)
        else:
            logger.exception("Page info error! Please check...")
            exit()
        try:
            user_name,user_id=get_user_info(driver)
            logger.info("Scraping Twitter User: "+user_name+" ID: "+user_id)
        except:
            logger.info("Scraping Twitter Account:"+account)
        keep_scrolling=True   # keep scroll if driver get the end of the page
        meet_history=False    # if meet scraped tweets
        while keep_scrolling and not meet_history:
            sleep(random.uniform(0.5,1.1))
            current_position = get_current_Y_offset(driver)   # get current position
            ## main func of scraping the tweets
            meet_history,driver, data, writer, tweet_ids= get_page_tweets(driver, account,data, writer, tweet_ids,logger,resume)

            # scroll 900 pixels
            driver=driver_scroling(driver, 900)
            if get_current_Y_offset(driver)==current_position:  #if already touch the end of the page
                keep_scrolling=False
                #logger.warning("End of the account")
                break

    data = pd.DataFrame(data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes','Retweets', 'Image link', 'Video link', 'Tweet URL'])

    # save_images
    if save_image:
        download_images(data, save_dir, logger)

    # save_videos
    if save_video:
        download_videos(data, save_dir, logger)

    return driver

def scrap_between_date(account,start_date,end_date,save_dir,headless=False,login=False,proxy=None,save_image=False,save_video=False,lang=None,continues=False,last_driver=None):

    logger = get_logger()

    ##################   init the webdriver   ####################
    driver = None
    if continues and last_driver:  # use current driver
        driver = last_driver
    else:
        driver = init_driver(headless, proxy, show_images=save_image)  # init a new driver
        if login:  # login twitter
            driver = login_website(driver, logger)
    ##############################################################

    # convert the datetime
    start_date=datetime.date(int(start_date.split("-")[0]),int(start_date.split("-")[1]),int(start_date.split("-")[2]))
    end_date = datetime.date(int(end_date.split("-")[0]), int(end_date.split("-")[1]), int(end_date.split("-")[2]))
    start_date_str=start_date.__format__('%Y-%m-%d')
    end_date_str=end_date.__format__('%Y-%m-%d')

    # to scrap tweets between start date and end date, we have not provided the " resume "
    csv_logfile_name = os.path.join(save_dir, account + "_" + start_date_str + "_"+end_date_str+".csv")
    check_dir(save_dir)

    tweet_ids = set()
    data = []

    try:
        open_user_page(driver,account,"main")
        user_name, user_id = get_user_info(driver)
        logger.info("Scraping Twitter User: " + user_name + " ID: " + account)
    except:
        logger.info("Scraping Twitter Account:" + account)

    with open(csv_logfile_name,'w',newline='',encoding='utf-8-sig') as f:
        header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes', 'Retweets','Image link', 'Video link', 'Tweet URL']
        writer = csv.writer(f)
        writer.writerow(header)

        max_date_str=end_date.__format__('%Y-%m-%d')
        start_date_str=start_date.__format__('%Y-%m-%d')
        open_search_page(driver, account, None, start_date_str, max_date_str, lang=lang)

        keep_scrolling = True  # keep scroll if driver get the end of the page
        meet_history = False  # if meet scraped tweets
        while keep_scrolling and not meet_history:
            sleep(random.uniform(0.5, 1.1))
            current_position = get_current_Y_offset(driver)  # get current position
            ## main func of scraping the tweets
            meet_history, driver, data, writer, tweet_ids = get_page_tweets(driver, account, data, writer, tweet_ids,logger,resume)

            # scroll 900 pixels
            driver = driver_scroling(driver, 900)
            if get_current_Y_offset(driver) == current_position:  # if already touch the end of the page
                keep_scrolling = False
                #logger.warning("End of the account")
                break

    data = pd.DataFrame(data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Emojis', 'Comments', 'Likes','Retweets', 'Image link', 'Video link', 'Tweet URL'])

    # save_images
    if save_image:
        download_images(data, save_dir,logger)

    # save_videos
    if save_video:
        download_videos(data, save_dir,logger)

    return driver
