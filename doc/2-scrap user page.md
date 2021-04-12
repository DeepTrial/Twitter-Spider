# scrap user page
To scrape the tweet or download images/videos between the start_date and max_date, just call the function:
```
from parsing_engine import interface

interface.scrap_main_page(
    account="twitter",    #twitter id
    save_dir="./saver/",
    headless=True,
    page_info="main" , #("with_replies","media","likes")  #choose user page (main)  or replies (with_replies) or media (media) or its likes (likes)
    save_image=True,
    save_video=true
)
```
You can find the csv file, images and videos in the dir: ./saver/
