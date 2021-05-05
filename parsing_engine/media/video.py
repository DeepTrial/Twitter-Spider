#! /usr/bin/env python3

# author @f-rog github

from datetime import datetime
import json
import logging
import re
import requests
import shutil
import sys
import os.path



class getVideo():
    def __init__(self, video_url):
        video_id = video_url.split('/')[5].split('?')[0] if 's?=' in video_url else video_url.split('/')[5]
        self.log = {}
        sources = {
            "video_url": "https://twitter.com/i/videos/tweet/" + video_id,
            "activation_ep": 'https://api.twitter.com/1.1/guest/activate.json',
            "api_ep": "https://api.twitter.com/1.1/statuses/show.json?id=" + video_id
        }
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'accept-language': 'es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5'}
        self.session = requests.Session()

        def send_request(self, url, method, headers):
            request = self.session.get(url, headers=headers) if method == "GET" else self.session.post(url,
                                                                                                       headers=headers)
            if request.status_code == 200:
                return request.text
            else:
                sys.exit(
                    "Bad request to {}, status code: {}.\nPlease sumbit an issue in the repo including this info.".format(
                        url, request.status_code))

        # get guest token
        token_request = send_request(self, sources["video_url"], "GET", headers)
        bearer_file = re.findall('src="(.*js)', token_request)
        file_content = send_request(self, str(bearer_file[0]), 'GET', headers)
        bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
        bearer_token = bearer_token_pattern.search(file_content)
        headers['authorization'] = bearer_token.group(0)
        self.log['bearer'] = bearer_token.group(0)
        req2 = send_request(self, sources['activation_ep'], 'post', headers)
        headers['x-guest-token'] = json.loads(req2)['guest_token']
        self.log['guest_token'] = json.loads(req2)['guest_token']
        # get link
        self.log['full_headers'] = headers
        api_request = send_request(self, sources["api_ep"], "GET", headers)
        try:
            videos = json.loads(api_request)['extended_entities']['media'][0]['video_info']['variants']
            self.log['vid_list'] = videos
            bitrate = 0
            for vid in videos:
                if vid['content_type'] == 'video/mp4':
                    if vid['bitrate'] > bitrate:
                        bitrate = vid['bitrate']
                        hq_video_url = vid['url']
            self.url = hq_video_url
        except:
            print(' No videos were found.')


def pretty_log(logdict):
    fn = 'log_file_twvdl-' + str(datetime.now()).replace(':', '-')[:19] + '.txt'
    log_dir = os.path.join('./log/', fn)
    with open(log_dir, 'w') as logfile:
        logfile.write(
            'These are the logs for the sequence of requests, if theres an issue, please submit a report with the contents of this file.\n')
        for k, v in logdict.items():
            logfile.write(
                '-*-*-*-*- start of ' + k + '-*-*-*-*-\n' + str(v) + '\n-*-*-*-*- end of ' + k + '-*-*-*-*-\n')
        print('Log saved at ./log/' + fn + '\nPlease submit a report with the content of said file.')


def save_file(url, ddir, filename):
    fn = url.split('/')[8].split('?')[0]
    if (filename):
        fn = filename if '.mp4' in filename else filename + '.mp4'
    op_dir = os.path.join(ddir, fn)
    with requests.get(url, stream=True) as r:
        with open(op_dir, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    #print('[' + Fore.GREEN + '+' + Style.RESET_ALL + '] ' + 'File successfully saved as ' + fn + ' !')



def download(index,url,save_path):
    dl = getVideo(url)
    try:
        if (dl.url):
            save_file(dl.url, save_path, index)
        else:
            print( 'Theres an internal error, hang on...')
            pretty_log(dl.log)

    except Exception as e:
        pretty_log(dl.log)
        print("Please also include details below: \n")
        logging.error('Error at %s', 'division', exc_info=e)

    del dl


def download_videos(data_frame,save_dir,logger,username=None):
    try:
        if not username:
            username = data_frame['UserName'].iloc[0]
        if not os.path.exists(save_dir + "/" + username):
            os.makedirs(save_dir + "/" + username)
        save_dir = os.path.join(save_dir, username)
    except:
        pass

    for i, url_video in enumerate(data_frame["Video link"]):
        if len(url_video)==0:
            continue
        try:
            data_time = data_frame['Timestamp'].iloc[i]
            data_time = data_time.split("T")[0]
            download(index=data_time+"-"+str(i),url=url_video,save_path=save_dir)
        except:
            logger.warning("Video at: " + url_video + " download failed.")
            #print('\r[' + Fore.YELLOW + 'WARNING' + Style.RESET_ALL + '] ' +  url_video + " video download failed")

# if __name__=="__main__":
#     download("2019-05-09","https://twitter.com/maou_0618/status/1126503764918063107","./media/")