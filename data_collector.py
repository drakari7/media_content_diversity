import time
import logging
import concurrent.futures
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as cOptions
from selenium.webdriver.firefox.options import Options as fOptions

# local imports
import tools

# logger options
logging.basicConfig(filename='logs_data_collection', filemode='w',
                    level=logging.INFO)


# --------Functions--------------------------
def wait_till_visible_xpath(driver, xpath):
    WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
    )


# Driver setup and options
def get_driver(browser: str):
    if browser == "chrome":
        DRIVER_PATH = "./drivers/chromedriver"
        # ADBLOCK_PATH = ""
        options = cOptions()
        options.add_argument('--headless')
        options.add_argument('--mute-audio')
        # options.add_extension(ADBLOCK_PATH)
        prefs = {"profile.managed_default_content_settings.images": 2}  # Don't load images
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(DRIVER_PATH, options=options)

    elif browser == "firefox":
        DRIVER_PATH = "./drivers/geckodriver"
        # ADBLOCK_PATH = "./extensions/ublock_origin.xpi"
        options = fOptions()
        options.add_argument('--headless')
        options.add_argument('--mute-audio')
        driver = webdriver.Firefox(DRIVER_PATH, options=options)
        # driver.install_addon(ADBLOCK_PATH)

    else:
        raise Exception("That browser is not valid")

    # time.sleep(5)           # Time for installing adblock
    return driver


def get_urls(driver, channel_name, time_range):
    """
    get_urls(driver, channel_name, time_range)

    args: driver - A webdriver for selenium
          channel_name - name of the channel currently in
          time_range - What time range we want the urls in

    Returns a tuple (urls, titles) of the videos in the current youtube page
    """

    posting_time_xpath = '//*[@id="metadata-line"]/span[2]'
    try:
        wait_till_visible_xpath(driver, posting_time_xpath)
    except:
        logging.exception("Could not load {0}'s youtube page properly".format(channel_name))

    posting_time = driver.find_elements_by_xpath(posting_time_xpath)
    logging.info("Collecting urls for channel {}".format(channel_name))

    # Scrolling down until we have the urls of all the videos in the time range
    last_vid = posting_time[-1]
    c1, c2,  c3 = 0, 0, 0
    while posting_time[-1].text != time_range:
        driver.execute_script("window.scrollBy(0,5000);")   # Scroll down

        try:
            posting_time = driver.find_elements_by_xpath(posting_time_xpath)
            c1 = 0
        except:
            c1 += 1
            logging.exception(f"Unknown error in URL collection - {channel_name}")
            if c1 == 10:
                logging.exception(f"Can't find URLs, stopping collection - {channel_name}")
                break
            continue
        
        if len(posting_time)%1000 >= 0 and len(posting_time)%1000 <= 60:
            logging.info(f"Last collected date = {posting_time[-1].text}, {len(posting_time)} URLS - {channel_name}")
        else:
            logging.info("Collected {0} URLs - {1}".format(len(posting_time), channel_name))

        if last_vid == posting_time[-1]:  # Break out of loop if stuck
            c2 += 1
            if c2 == 10:
                time.sleep(5)
                c2 = 0
                c3 += 1
            if c3 == 10:
                logging.warning(f"Stuck at finding new URLs, breaking... - {channel_name}")
                break
        else:
            c2, c3 = 0, 0
            last_vid = posting_time[-1]
        logging.info(c2)

        time.sleep(0.15)     # Give time to load

    # Collecting all relevant video urls
    titles = driver.find_elements_by_id("video-title")
    urls = [title.get_attribute("href") for title in titles]
    titles = [i.text for i in titles]
    return (urls, titles)


def process_urls(driver, channel_name, file_name, urls) -> None:
    # processing each of the urls 1 by 1, if we run into some error,
    # then we skip the video
    skipped_videos_count = 0

    with open(file_name, "w") as write_file:
        for idx, url in enumerate(urls):
            try:
                line = _process_url(driver, url)
            except:
                logging.exception("Corrupted URL : {0}, video no. {1}, {2}".format(url, idx, channel_name))
                skipped_videos_count += 1
                continue

            print(line, file=write_file)
            logging.info("Video No. {0} processed for {1}".format(idx, channel_name))

    print("Total videos skipped for channel {0} = {1}".format(channel_name, skipped_videos_count))

# Actually scraping the data
def _process_url(driver, url):
    driver.get(url)

    # Wait for title to load, if can't then throw error
    title_xpath = '//*[@id="container"]/h1/yt-formatted-string'
    wait_till_visible_xpath(driver, title_xpath)
    title = driver.find_element_by_xpath(title_xpath).text

    views_xpath = '//*[@id="count"]/ytd-video-view-count-renderer/span[1]'
    views = driver.find_element_by_xpath(views_xpath).text

    date_xpath = '//*[@id="info-strings"]/yt-formatted-string'
    date = driver.find_element_by_xpath(date_xpath).text

    # duration_xpath = "//span[@class='ytp-time-duration']"
    # duration = driver.find_element_by_xpath(duration_xpath).text

    keywords = driver.find_element_by_name("keywords")
    keywords = keywords.get_attribute("content")
    keywords = ' '.join(keywords.splitlines())

    description_xpath = '//*[@id="description"]/yt-formatted-string'
    description = driver.find_element_by_xpath(description_xpath).text
    description = ' '.join(description.splitlines())

    return '\\#\\'.join([title, views, date, keywords, description])


def scrape_channel_data(channel_link):
    cs_time = time.perf_counter()

    channel_name = tools.get_channel_name(channel_link)         # Output file handling
    file_name = 'channel_data/' + channel_name + '.tmp'

    with get_driver(browser="chrome") as driver:
        driver.get(channel_link)
        try:
            video_urls, _ = get_urls(driver, channel_name, time_range="2 days ago")
        except:
            logging.exception(f"Getting URL function failed! - {channel_name}")
            raise

        elapsed_time = time.perf_counter() - cs_time
        print("Total number of urls found for channel {0} = {1} in {2}".format(channel_name, len(video_urls),  tools.format_time(elapsed_time)))

        process_urls(driver, channel_name, file_name, video_urls)

        final_time = time.perf_counter() - cs_time
        print("Total time taken for channel {0} = {1}".format(channel_name, tools.format_time(final_time)))


# ------------------ Start of Main Code -------------------------------
def main():
    g_start = time.perf_counter()

    # channels = tools.get_channel_links()[1:2]
    channels = tools.temp_get_channels()
    # channels = tools.get_testing_channel()              # Uncomment for testing

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrape_channel_data, channels)

    g_end = time.perf_counter()
    print("Total overall time = {}".format(tools.format_time(g_end - g_start)))


if __name__ == "__main__":
    main()
