from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import datetime
import logging
import sys

### local imports
import tools

### logger options
logging.basicConfig(filename = 'logs', filemode='w', level = logging.INFO)

PATH = "/Applications/chromedriver"


#--------Functions--------------------------
def wait_till_visible_xpath(driver,xpath):
    WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
    )
    
def scrape_channel_data(channel_link):
    cs_time = time.time()

    ### Driver setup and options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--mute-audio')
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(PATH, options=options)

    driver.get(channel_link)

    ### Output file handling 
    channel_name = tools.get_channel_name(channel_link)
    file_name = 'channel_data/' + channel_name + '.csv'
    write_file = open(file_name, "w")

    ### Collecting posting time data of videos
    posting_time_xpath = '//*[@id="metadata-line"]/span[2]'
    try:
        wait_till_visible_xpath(driver, posting_time_xpath)
    except:
        logging.info("Could not load {0}'s youtube page properly".format(channel_name))

    posting_time = driver.find_elements_by_xpath(posting_time_xpath)

    ### Scrolling down until we have the urls of all the videos in the time range
    logging.info("Collecting URLs")

    time_range = "3 months ago"
    while posting_time[-1].text != time_range:
        #move pixels to bottom of screen and force loading of more videos
        driver.execute_script("window.scrollBy(0,5000);")

        posting_time = driver.find_elements_by_xpath(posting_time_xpath)
        logging.info("Collected {0} URLs".format(len(posting_time)))

        # Allow the channel time to load more videos
        time.sleep(0.2)
    
    ### Collecting all relevant video urls
    posting_time = driver.find_elements_by_xpath(posting_time_xpath)
    video_titles = driver.find_elements_by_id("video-title")
    # removing some extra videos
    idx = 0
    for idx in range(len(posting_time)):
        if posting_time[idx] == time_range:
            break

    video_titles = video_titles[:idx]
    video_urls = [ title.get_attribute("href") for title in video_titles ]
    video_titles = [ i.text for i in video_titles ]

    elapsed_time = time.time() - cs_time
    print("Total number of urls found for channel {0} = {1} in {2} seconds".format(channel_name, len(video_urls),  elapsed_time))


    # processing each of the urls 1 by 1, if we run into some error, then we skip the video
    skipped_videos_count = 0

    for i,url in enumerate(video_urls):
        driver.get(url)
        
        ### Wait for title to load, if can't then print error and continue
        title_xpath ='//*[@id="container"]/h1/yt-formatted-string' 
        try:
            wait_till_visible_xpath(driver,title_xpath)
        except:
            print("Something went wrong with the video: " + video_titles[i], file = sys.stderr)
            print("Video ignored!", file = sys.stderr)
            logging.info("Corrupted URL : {0}".format(url))
            skipped_videos_count += 1
            continue

        ### Actually scraping the data
        title = driver.find_element_by_xpath(title_xpath).get_attribute("innerText")

        views_xpath = '//*[@id="count"]/ytd-video-view-count-renderer/span[1]'
        views = driver.find_element_by_xpath(views_xpath).get_attribute("innerText")

        date_xpath = '//*[@id="date"]/yt-formatted-string'
        date = driver.find_element_by_xpath(date_xpath).get_attribute("innerText")

        keywords = driver.find_element_by_name("keywords").get_attribute("content")
        keywords = ' '.join(keywords.splitlines())

        description_xpath = '//*[@id="description"]/yt-formatted-string'
        description = driver.find_element_by_xpath(description_xpath).get_attribute("innerText")
        description = ' '.join(description.splitlines())

        print("{0}\\#\\{1}\\#\\{2}\\#\\{3}\\#\\{4}".format(title,views,date,keywords,description), file = write_file )
        logging.info("Video No. {0} processed: URL - {1}   -   Video {2}".format(i, url, title))

    print("Total videos skipped for channel {0} = {1}".format(channel_name, skipped_videos_count))
    write_file.close()
    driver.close()

#------------------ Start of Main Code -------------------------------
def main():
    g_start = time.time()

    # For testing purposes, use channel 11, syntax is channels[10:]
    channels = tools.get_channel_links()
    channels = channels[10:]

    for channel in channels:
        channel_name = tools.get_channel_name(channel)

        t_start = time.time()
        scrape_channel_data(channel)
        t_end = time.time()
        print("Time taken for channel {0} = {1} s".format(channel_name,t_end-t_start))

    g_end = time.time()
    print("Total time = {}".format(g_end - g_start))


if __name__ == "__main__":
    main()

