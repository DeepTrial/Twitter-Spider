# T-Scraper: A twitter scraper for python 

compared with other twitter scrapers, T-Scraper is more:
- simple
- unlimited
- without any authentications

This tool is based on:
- [Sweet](https://github.com/Altimis/Scweet) as the basic method of twitter scraper
- [twitter2mp4](https://github.com/f-rog/twitter2mp4) as the component of video downloader

This repository provide an alternative legal tool to scrap tweets between two given dates (start_date and max_date), for a given language and list of words or account name, and saves a csv file containing all the scraped data :

[UserScreenName, UserName, Timestamp, Text, Emojis, Comments, Likes, Retweets, Image link, Video link, Tweet URL]

**It is also possible to download and save the images and videos from the links** by passing the argument save_images = True, save_videos=True. 

T-Scraper uses only selenium to scrape data. Authentications is required in the case of followers/following scraping. It is recommended to log in with a new account (if the list of followers is very long, **it is possible that your account will be banned**). To log in to your account, you need to enter your username and password in .env file. You can control the wait parameter in the get_users_followers and get_users_following functions.

## First time to use

For the first time, you need to create a `.env` file in the same level directory of the main.py, and save your login information in this file:
```
TWITTER_USERNAME=your_user_name_or_email
TWITTER_PASSWORD=your_password
```
In addition, I highly recommand to set the -p 1(headless=False) for the first time of login to make sure you really login successfully.

**For more information about installation and usage, Please refer to the /doc/ dir**

## To-do Next:
- bug fixed
- add the func for downloading GIFs
- proxy for downloading
