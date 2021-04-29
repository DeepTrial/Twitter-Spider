#! /usr/bin/env python3

import os
import requests
import urllib
import threading

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


def download_func(image_resource):

    for (image_url,image_filepath) in image_resource:
        try:
            urllib.request.urlretrieve(image_url,image_filepath)
        except:
            try:
                imgres = requests.get(image_url)
                with open(image_filepath, "wb") as f:
                    f.write(imgres.content)
            except:
                print("Image at: " + image_url + " download failed.")

    return 0

def download_images_multithread(data_frame, save_dir,logger):
    image_resource=[]
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

            image_url=url.split("name")[0]+"name=large"
            image_filepath=dst_dir + '/'+data_time+'_post-'+str(i+ 1)+'-' + str(j + 1) + ".jpg"

            image_resource.append((image_url,image_filepath))

    # num_cores = int(mp.cpu_count())
    # logger.info("There are: " + str(num_cores) + " cores in this pc.")
    # pool = mp.Pool(4)
    #
    # param_dict = {'task1': image_resource[:len(image_resource)//4],
    #               'task2': image_resource[len(image_resource)//4:len(image_resource)//2],
    #               'task3': image_resource[len(image_resource)//2:len(image_resource)//4*3],
    #               'task4': image_resource[len(image_resource)//4*3:]}
    th_lst=[[image_resource[:len(image_resource)//4]],[image_resource[len(image_resource)//4:len(image_resource)//2]],[image_resource[len(image_resource)//2:len(image_resource)//4*3]],[image_resource[len(image_resource)//4*3:]]]
    for lst in th_lst:
        threading.Thread(target=download_func, args=(lst)).start()

