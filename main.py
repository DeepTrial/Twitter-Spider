#! /usr/bin/env python3

import argparse

from parsing_engine import interface
from parsing_engine.login.login_twitter import login_pwd

parser = argparse.ArgumentParser(description='T-Scraper: A Twitter scraper that overrides some limits of official Twitter API')
parser.add_argument("-as", "--accounts", default=None,help='A file with each line a user ID or link to their main page.')
parser.add_argument("-a", "--account", default="POTUS",help='Ignored if "-as" provided. Single account that you want, default is "POTUS". DO NOT enter the @ mark.')
parser.add_argument("-i", "--image", default=0, type=int,help='Whether to save images. 0 for no (default), non-zero int for yes.')
parser.add_argument("-m", "--mode", default="main",help='Choose mode: "main" (default) for whatever tweets on main page; "media" for only images and videos on main page; "date" for a specified range')
parser.add_argument("-p", "--pop", default=0, type=int,help='Whether to show pop-up browser window. 0 for no (default), non-zero int for yes.')
parser.add_argument("-sd", "--savedir", default="./saver/",help='The directory for saving the outputs. Default to be ./saver/')
parser.add_argument("-v", "--video", default=0, type=int,help='Whether to save videos. 0 for no (default), non-zero int for yes.')
parser.add_argument("-r","--resume",default=0,type=int,help='whether to resume the process according to the current csv file')
parser.add_argument("-b", "--begin", default="2021-1-1",help='Under "date" mode, the begin date of search. Default to be Jan 1, 2021.')
parser.add_argument("-e", "--end", default="2021-1-10",help='Under "date" mode, the end date of search. Default to be Jan 10, 2021.')
parser.add_argument("-l", "--lang", default=None,help='Under "date" mode, filter the language you want. "en" for English, "es" for Spanish, "fr" for French, "zh" for Chinese, no filter for all languages (default).')
parser.add_argument("-fst", "--first", default=0,type=int,help='If it is the first time to login your account')
args = parser.parse_args()

def scrap_base(account,continues=False,driver=None):
    '''
    base function of scrap tweets. According to the parameter, choose the related solution.
    '''
    if args.mode != "date":
        driver=interface.scrap_main_page(
            account=account,
            save_dir=args.savedir,
            headless=False if args.pop else True,
            page_info=args.mode,
            login=True,
            resume=args.resume,
            save_image=args.image,
            save_video=args.video,
            continues=continues,
            last_driver=driver
        )
    elif args.mode == "date":
        driver=interface.scrap_between_date(
            account=account,
            start_date=args.begin,
            end_date=args.end,
            save_dir=args.savedir,
            headless=False if args.pop else True,
            save_image=args.image,
            save_video=args.video,
            lang=args.lang,
            continues=continues,
            last_driver=driver
        )
    return driver

def scrap_one_account(account):
    driver=scrap_base(account)
    driver.close()

def scrap_account_lists(account_list):
    driver=None
    for i in range(len(account_list)):
        driver=scrap_base(account_list[i],continues=True,driver=driver)
    driver.close()


if args.first:
    driver=None
    driver=login_pwd(driver,True)
    driver.close()



if args.accounts!=None:
    cand_accounts=[]
    with open(file=args.accounts, mode="r", encoding="utf-8") as f:
        for line in f:
            account = line.split("twitter.com/")[-1].strip()
            if len(account)>1:
                cand_accounts.append(account)
                #scrap(account)

    scrap_account_lists(cand_accounts)
else:
    scrap_one_account(args.account)