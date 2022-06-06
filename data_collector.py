import time
import logging
import concurrent.futures
import os
import shutil
from datetime import date, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# local imports
import tools as tl

# logger options
logging.basicConfig(filename='log_pipeline', filemode='w',
        format='%(asctime)s  %(levelname)s:%(message)s',
        level=logging.INFO,
        datefmt='%H:%M:%S')
# Globals
data_dir = "data/"
file_path = lambda x: data_dir + x + '.hsv.new'
today = date.today()


# --------Functions--------------------------
def wait_till_visible_xpath(driver, xpath):
    WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))


def get_driver():
    """
    Returns driver (google chrome driver) object
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--mute-audio')
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    os.environ['WDM_LOG'] = '0'
    driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
            )
    return driver


def get_urls(driver: WebDriver, channel_name, time_range):
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
        logging.exception(f"Could not load {channel_name}'s youtube page properly")

    posting_time = driver.find_elements(By.XPATH, posting_time_xpath)
    logging.info(f"Collecting urls for channel {channel_name}")

    range_pos = tl.time_pos(time_range)
    stuck_counter = 0
    prev_len = 0
    # Scrolling down until we have the urls of all the videos in the time range
    while tl.time_pos(posting_time[-1].text) <= range_pos+1:
        driver.execute_script("window.scrollBy(0,5000);")   # Scroll down
        try:
            posting_time = driver.find_elements(By.XPATH, posting_time_xpath)
        except:
            logging.exception(f"Unknown error in URL collection - {channel_name}")
            continue

        if len(posting_time) == prev_len:
            stuck_counter += 1
            if stuck_counter == 50:
                time.sleep(10)
                raise
        else:
            stuck_counter = 0
        prev_len = len(posting_time)
        logging.info(f"Collected {len(posting_time)} URLs - {channel_name}")
        time.sleep(0.2)     # Give time to load

    time.sleep(0.3)         # time to stabilise page

    # Determine precisely how many videos we want for given time range
    posting_time = driver.find_elements(By.XPATH, posting_time_xpath)
    idx = len(posting_time) - 1
    while tl.time_pos(posting_time[idx].text) > range_pos:
        idx -= 1

    # Collecting all relevant video urls
    t1 = time.perf_counter()
    titles = driver.find_elements(By.ID, "video-title")[:idx+1]
    t2 = time.perf_counter()
    logging.info(f"time taken to get {idx+1} elements {tl.format_time(t2-t1)} - {channel_name}")
    urls = [title.get_attribute("href") for title in titles]
    titles = [i.text for i in titles]
    return (urls, titles)


# Actually scraping the data
def _process_url(driver: WebDriver, url, time_range):
    if 'shorts' in url:
        return None
    driver.get(url)

    # Wait for title to load, if can't then throw error
    title_xpath = '//*[@id="container"]/h1/yt-formatted-string'
    wait_till_visible_xpath(driver, title_xpath)
    title = driver.find_element(By.XPATH, title_xpath).get_attribute("innerText")

    views_xpath = '//*[@id="count"]/ytd-video-view-count-renderer/span[1]'
    views = driver.find_element(By.XPATH, views_xpath).get_attribute("innerText")

    date_xpath = '//*[@id="info-strings"]/yt-formatted-string'
    tmp = driver.find_element(By.XPATH, date_xpath).get_attribute("innerText")

    # duration_xpath = "//span[@class='ytp-time-duration']"
    # duration = driver.find_elements(By.XPATH, duration_xpath).get_attribute("innerText")

    keywords = driver.find_element(By.NAME, "keywords")
    keywords = keywords.get_attribute("content")
    keywords = ' '.join(keywords.splitlines())

    description_xpath = '//*[@id="description"]/yt-formatted-string'
    description = driver.find_element(By.XPATH, description_xpath).get_attribute("innerText")
    description = ' '.join(description.splitlines())

    try:
        vid_date = tl.parse_date(tmp)
    except:
        return None

    start_date = str(today - timedelta(tl.time_pos(time_range)))
    end_date = str(today - timedelta(1))
    
    if vid_date < start_date or vid_date > end_date:
        return None

    return '\\#\\'.join([title, views, vid_date, keywords, description])


def process_urls(driver, channel_name, urls, time_range) -> tuple[float, list[str]]:
    # processing each of the urls 1 by 1, if we run into some error,
    # then we skip the video
    skipped_videos_count, total_videos_count, continuous_skipped = 0, 0, 0
    file_data = []

    for idx, url in enumerate(urls):
        total_videos_count += 1
        try:
            line = _process_url(driver, url, time_range)
            continuous_skipped = 0
        except:
            logging.error(f"Corrupted URL : {url}, video no. {idx+1}, {channel_name}")
            skipped_videos_count += 1
            continuous_skipped += 1

            # If 10 videos are skipped continuously, return failure
            if continuous_skipped == 10:
                logging.info(f"10 failures in a row for {channel_name}, aborting...")
                time.sleep(10)
                return 1.0, []
            continue

        if line:
            file_data.append(line)
        logging.info(f"Video No. {idx+1} processed for {channel_name}")

    # ratio of videos which were skipped
    fail_rate = skipped_videos_count/total_videos_count
    return fail_rate, file_data[::-1]


def scrape_channel_data(channel_link, time_range) -> None:
    channel_name = tl.get_channel_name(channel_link)    # Output file handling

    # Create data directory if doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    file_name = data_dir + channel_name + '.hsv.new'

    with get_driver() as driver:
        driver.get(channel_link)
        try:
            video_urls, _ = get_urls(driver, channel_name, time_range)
        except:
            logging.exception(f"Getting URL function failed! - {channel_name}")
            raise

    fail_rate, counter = 1, 0
    while fail_rate > 0.2 and counter < 5:
        counter += 1
        with get_driver() as driver:
            fail_rate, data = process_urls(driver, channel_name, 
                        video_urls, time_range)
        time.sleep(5)

    if fail_rate < 0.2:
        with open(file_name, "w") as f:
            f.write("\n".join(data))
        logging.info(f"Channel finished successfully - {channel_name}")

def append_data(links):
    new_paths = [file_path(tl.get_channel_name(c)) for c in links]

    for new_path in new_paths:
        old_path = new_path[:-4]
        # Make sure older file exists
        if not os.path.exists(old_path):
            with open(old_path, 'w'): pass

        with open(new_path, 'r') as rf:
            data = rf.read()
        with open(old_path, 'a') as af:
            af.write(data)
        os.remove(new_path)

def collect_all_data(links, n_days: int, n_workers=6):
    logging.info(f"Launching collect data function")
    time_range = str(n_days) + " days ago"
 
    # Make backup of previous data
    shutil.rmtree('data_backup', ignore_errors=True)
    shutil.copytree('data', 'data_backup')

    # Define useful lambdas
    is_collected = lambda x: os.path.isfile(x) and os.path.getsize(x) > 0

    links_dict = {file_path(tl.get_channel_name(link)):link for link in links}

    # keep collecting until we get clean copies for all
    # if it fails 5 times, then program terminates
    attempts = 0
    while links_dict and attempts < 5:
        attempts += 1
        links = links_dict.values()
        ranges = [time_range] * len(links)
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
            executor.map(scrape_channel_data, links, ranges)

        for fp in list(links_dict.keys()):
            if is_collected(fp):
                del links_dict[fp]

# ------------------ Start of Main Code -------------------------------
def main():
    links = tl.get_temp_links()
    collect_all_data(links, 44)
    append_data(links)


if __name__ == "__main__":
    main()
