#! /usr/bin/env python3

import argparse

from parsing_engine import interface


parser = argparse.ArgumentParser(description='T-Scraper: A Twitter scraper that overrides some limits of official Twitter API')

parser.add_argument("-a", "--account", default=None,\
    help='Account that you want, e.g. "POTUS". DO NOT enter the @ mark.')
parser.add_argument("-as", "--accounts", default=None,\
    help='Ignored if "-a" provided. A file with each line a user ID or link to their main page.')
parser.add_argument("-i", "--image", default=0, type=int,\
    help='Whether to save images. 0 for no (default), non-zero int for yes.')
parser.add_argument("-m", "--mode", default="main",\
    help='Choose mode: "main" (default) for whatever tweets on main page; "date" for a specified range')
parser.add_argument("-p", "--pop", default=0, type=int,\
    help='Whether to show pop-up browser window. 0 for no (default), non-zero int for yes.')
parser.add_argument("-sd", "--savedir", default="./saver/",\
    help='The directory for saving the outputs. Default to be ./saver/')
parser.add_argument("-v", "--video", default=0, type=int,\
    help='Whether to save videos. 0 for no (default), non-zero int for yes.')

parser.add_argument("-b", "--begin", default="2021-1-1",\
    help='Under "date" mode, the begin date of search. Default to be Jan 1, 2021.')
parser.add_argument("-e", "--end", default="2021-1-10",\
    help='Under "date" mode, the end date of search. Default to be Jan 10, 2021.')
parser.add_argument("-l", "--lang", default=None,\
    help='Under "date" mode, filter the language you want. "en" for English, "es" for Spanish, "fr" for French, "zh" for Chinese, no filter for all languages (default).')

args = parser.parse_args()

def scrap(account):
    if args.mode == "main":
        interface.scrap_main_page(
            account=account,
            save_dir=args.savedir,
            headless=False if args.pop else True,
            page_info="main",
            login=True,
            resume=True,
            save_image=args.image,
            save_video=args.video
        )
    elif args.mode == "date":
        interface.scrap_between_date(
            account=account,
            start_date=args.begin,
            end_date=args.end,
            save_dir=args.savedir,
            headless=False if args.pop else True,
            save_image=args.image,
            save_video=args.video,
            lang=args.lang
        )

if args.account!=None:
    scrap(args.account)
elif args.accounts!=None:
    with open(file=args.accounts, mode="r", encoding="utf-8") as f:
        for line in f:
            account = line.split("twitter.com/")[-1].strip()
            if len(account)>1:
                scrap(account)