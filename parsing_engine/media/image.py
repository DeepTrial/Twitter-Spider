#! /usr/bin/env python3

from colorama import init, Fore, Style
import os
import requests
import urllib

init()


def download_images(data_frame, save_dir,logger):
    for i, url_v in enumerate(data_frame["Image link"]):
        username = data_frame['UserName'].iloc[0]
        if not username:
            username=data_frame['UserScreenName'].iloc[0]
        if not os.path.exists(save_dir + "/" + username):
            os.makedirs(save_dir + "/" + username)
        dst_dir = os.path.join(save_dir, username)

        for j, url in enumerate(url_v):
            if ("video" in url ) or ("profile" in url):
                continue
            data_time=data_frame['Timestamp'].iloc[i]
            data_time=data_time.split("T")[0]
            try:
                newurl=url.split("name")[0]+"name=large"  #download iamge for original size
                urllib.request.urlretrieve(newurl, dst_dir + '/'+data_time+'_post-'+str(i+ 1)+'-' + str(j + 1) + ".jpg")

            except:
                try:
                    newurl = url.split("name")[0] + "name=large"
                    imgres = requests.get(newurl)
                    with open(dst_dir + '/' + data_time + '_post-' + str(i + 1) + '-' + str(j + 1) + ".jpg", "wb") as f:
                        f.write(imgres.content)
                except:
                    logger.warning("Image at: "+newurl+" download failed.")
                    #print('\r[' + Fore.YELLOW + 'WARNING' + Style.RESET_ALL + '] ' + newurl + " image download error")