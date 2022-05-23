from PIL import Image
import numpy as np
import time
from dateutil import parser
from datetime import datetime
import re
import os

# returns the name of the channel from its youtube link
def get_channel_name(channel_link: str):
    channel_name = channel_link.split('/')[4]
    return channel_name


# Reads returns all channel links
def get_channel_links():
    with open("./text_files/channel_ytlinks") as f:
        links = [link[:-1] for link in f.readlines()]
    return links


def get_temp_links():
    links = get_channel_links()
    links = links[22:23]
    return links


def get_testing_channel():
    return ['https://www.youtube.com/c/DDIndia/videos']


# check if a string can be converted to int
def is_int(x: str) -> bool:
    try:
        int(x)
        return True
    except ValueError:
        return False


# Convert seconds to hr, min, seconds format
def format_time(t: float):
    t = int(t)
    h, m, s = t//3600, (t//60)%60, t%60
    if h == 0:
        return str(m) + " mins, " + str(s) + " s"
    else:
        return str(h) + " hrs, " + str(m) + " mins, " + str(s) + " s"

# Concatenates regex search patterns
def concat_patterns(*args: str) -> str:
    ans = args[0]
    for arg in args[1:]:
        ans += "|" + arg
    return ans

# Fails if date cannot be parsed
def parse_date(s: str):
    '''
    Formats the date from '26 Jan, 22' format to
    2022-01-26 format. Allows comparision of dates etc.
    '''

    p1 = r"^Streamed live on "
    p2 = r"^Premiered on "
    p3 = r"^Started streaming on "

    s = re.sub(concat_patterns(p1, p2, p3), '', s)
    ans = parser.parse(s).strftime("%Y-%m-%d")
    return ans

def time_pos(given_time: str):
    """
    Wrapper function to implement time relative ordering
    of strings like '1 week ago' and '2 days ago'
    """
    given_time = re.sub(r"^Streamed", "", given_time)

    if "hour" in given_time or "minute" in given_time:
        return 0

    line = given_time.split()
    num = int(line[0])
    v = line[1].removesuffix('s')

    time_scales = {
            'day' : 1,
            'week' : 7,
            'month' : 30,
            'year' : 365,
    }

    return num*time_scales[v]


# Return a blank white image to save
def get_blank_image():
    a = np.full((480, 640, 3), 255, dtype=np.uint8)
    image = Image.fromarray(a, "RGB")
    return image

# return a list containing only distinct elements in original order
def make_unique(a):
    seen = set()
    ans = []
    for x in a:
        if x not in seen:
            ans.append(x)
            seen.add(x)
    return ans

# Decorator to time function calls
def timer(func):
    def wrapper(*args, **kwargs):
        t1 = time.perf_counter()
        result = func(*args, **kwargs)
        t2 = time.perf_counter()
        print(f'Time taken by {func.__name__!r} is {format_time(t2-t1)}')
        return result
    return wrapper

# Add elementwise y[i] to x[i]
def add_vector(x, y):
    for i in range(len(y)):
        x[i] += y[i]

# Moved to keep track of older legacy code
def load_wiki_pages():
    wiki_pages = set()
    multistream_path = '../wikipedia_data/multistream_index.txt'
    with open(multistream_path) as f:
        for line in f.readlines():
            page = line.split(":")[2][:-1]
            wiki_pages.add(page)

    return wiki_pages

# Get the root directory of the project on any system
def get_root_dir():
    curr_file = __file__
    root_dir = '/'.join(curr_file.split('/')[:-1]) + '/'
    return root_dir

def get_cache_dir():
    dir = get_root_dir() + 'cache/'
    return dir

def label_dates(dates):
    temps = [datetime.strptime(a, '%Y-%m-%d') for a in dates]
    return [datetime.strftime(a, '%b %-d') for a in temps]

def cutoff_cname(cname):
    if len(cname) < 13:
        return cname
    else:
        return cname[:11] + '..'


# ----------------Testing----------------
def main():
    l = get_channel_links()
    k = get_temp_links()

    for i, lin in enumerate(l):
        print(i, get_channel_name(lin))

    print()

    for i, lin in enumerate(k):
        print(i, get_channel_name(lin))


if __name__ == "__main__":
    main()
