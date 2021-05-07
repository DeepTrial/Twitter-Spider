#! /usr/bin/env python3

import re


def open_user_page(driver,account,page_info):
    if page_info=="main":
        page_info=""
    driver.get('https://twitter.com/' + account+"/"+page_info)

def get_user_info(driver):
    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    if len(page_cards)>0:
        card=page_cards[0]
        try:
            username = card.find_element_by_xpath('.//span').text
            userID = card.find_elements_by_xpath('.//span[contains(text(), "@")]')[-1].text
            return username, userID
        except:
            return None,None


def open_search_page(driver,from_account,to_account,start_date_str,end_date_str,hashtag=None,words=None,lang=None):
    from_account = "(from%3A" + from_account + ")%20" if from_account is not None else ""
    to_account = "(to%3A" + to_account + ")%20" if to_account is not None else ""
    hash_tags = "(%23" + hashtag + ")%20" if hashtag is not None else ""

    if words is not None:
        # words = str(words).split("//")
        words = "(" + str('%20OR%20'.join(words)) + ")%20"
    else:
        words = ""

    if lang is not None:
        lang = 'lang%3A' + lang
    else:
        lang = ""

    end_date = "until%3A" + end_date_str + "%20"
    start_date = "since%3A" + start_date_str + "%20"

    # print('https://twitter.com/search?q=' + words + from_account + to_account + hash_tags + end_date + start_date + lang + '&src=typed_query' + display_type)
    driver.get('https://twitter.com/search?q=' + words + from_account + to_account + hash_tags + end_date + start_date + lang + '&src=typed_query&f=live')


langs_video={"zh":"次观看","en":"views"}

def get_single_tweet(card, lang="en"):
    """Extract data from tweet card"""
    image_links = []
    video_url=""
    try:
        username = card.find_element_by_xpath('.//span').text
    except:
        return

    try:
        #to prevent username contains @, we find all possible userid, the actual userid is the last one
        userID = card.find_elements_by_xpath('.//span[contains(text(), "@")]')[-1].text
    except:
        return

    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except:
        return

    try:
        comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except:
        comment = ""

    try:
        responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except:
        responding = ""

    text = comment + responding

    try:
        reply_cnt = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
    except:
        reply_cnt = 0

    try:
        retweet_cnt = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    except:
        retweet_cnt = 0

    try:
        like_cnt = card.find_element_by_xpath('.//div[@data-testid="like"]').text
    except:
        like_cnt = 0

    try:
        elements = card.find_elements_by_xpath('.//div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/")]')
        for element in elements:
            image_links.append(element.get_attribute('src'))
    except:
        image_links = []


    try:
        promoted = card.find_element_by_xpath('.//div[2]/div[2]/[last()]//span').text == "Promoted"
    except:
        promoted = False
    if promoted:
        return

    # get a string of all emojis contained in the tweet
    try:
        emoji_tags = card.find_elements_by_xpath('.//img[contains(@src, "emoji")]')
    except:
        return
    emoji_list = []
    for tag in emoji_tags:
        try:
            filename = tag.get_attribute('src')
            emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
        except AttributeError:
            continue
        if emoji:
            emoji_list.append(emoji)
    emojis = ' '.join(emoji_list)

    # tweet url
    try:
        element = card.find_element_by_xpath('.//a[contains(@href, "/status/")]')
        tweet_url = element.get_attribute('href')
        if langs_video[lang.lower()] in text or (len(image_links)==1 and "pu/img" in image_links[0]):
            video_url = "https://twitter.com/i/status/"+tweet_url.split("/")[-1]
            image_links=[]
    except:
        return

    tweet = (username, userID, postdate, text, emojis, reply_cnt, retweet_cnt, like_cnt, image_links,video_url, tweet_url)
    return tweet

def get_page_tweets(driver,account,data,writer,tweet_ids,logger,resume,page_info):
    history_count=0
    meet_history=False

    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for card in page_cards:
        tweet = get_single_tweet(card)
        if tweet and ((page_info!="likes" and tweet[1]=='@'+account) or page_info=="likes"):
            # check if the tweet is unique
            # Each user has a unique ID, and cannot publish multiple tweets simultaneously
            tweet_id = tweet[2] + tweet[1] # Timestamp+UserID
            # Alternatively: tweet_id = tweet[-1] # URL
            if tweet_id not in tweet_ids:
                history_count=0
                tweet_ids.add(tweet_id)
                data.append(tweet)
                writer.writerow(tweet)
                logger.info("Found tweet made at "+str(tweet[2]))
            else:
                history_count+=1
        if history_count>=10 and resume:  # if there are 5 continuous saved tweets
            meet_history=True
            logger.info("Find all new tweets!")
            break
    return meet_history,driver, data, writer, tweet_ids
