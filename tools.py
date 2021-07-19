# returns the name of the channel from its youtube link
def get_channel_name(channel_link: str):
    channel_name = channel_link.split('/')[4]
    return channel_name


# Reads and collects links of youtube channels from their files
def get_channel_links():
    with open("english_channels_ytlinks", "r") as file1:
        channel_links = [link[:-1] for link in file1.readlines()]

    with open("hindi_channels_ytlinks", "r") as file2:
        channel_links.extend([link[:-1] for link in file2.readlines()])
    return channel_links

def temp_get_channels():
    chans = get_channel_links()
    chans = chans[4:5] + chans[6:7]
    return chans


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
    channels = get_testing_channel()
    print(channels)


if __name__ == "__main__":
    main()
