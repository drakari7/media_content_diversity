# returns the name of the channel from its youtube link
def get_channel_name(channel_link: str):
    channel_name = channel_link.split('/')[4]
    return channel_name


def get_english_links():
    with open("text_files/english_channels_ytlinks", "r") as file1:
        links = [link[:-1] for link in file1.readlines()]
    return links 


def get_hindi_links():
    with open("text_files/hindi_channels_ytlinks", "r") as file1:
        links = [link[:-1] for link in file1.readlines()]
    return links 


# Reads returns all channel links
def get_channel_links():
    channel_links = get_english_links() + get_hindi_links()
    return channel_links


def get_testing_channel():
    return ['https://www.youtube.com/c/TodayontheKoreanServer/videos']


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


# ----------------Testing----------------
def main():
    channels = get_channel_links()
    print(channels)


if __name__ == "__main__":
    main()
