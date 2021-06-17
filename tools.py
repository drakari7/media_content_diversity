### Contains different functions that are used throughout the code

## returns the name of the channel from its youtube link
def get_channel_name(channel_link: str):
    channel_name = channel_link.split('/')[4]
    if ( channel_name == "videos" ):
        channel_name = channel_link.split('/')[3]
    return channel_name

## Reads and collects links of youtube channels from their files
def get_channel_links():
    with open("english_channels_ytlinks", "r") as f1:
        channel_links = [link[:-1] for link in f1.readlines()]

    with open("hindi_channels_ytlinks", "r") as f2:
        channel_links.extend( [link[:-1] for link in f2.readlines()])
    return channel_links


## check if a string can be converted to int
def is_int(a: str) -> bool:
    try:
        int(a)
        return True
    except ValueError:
        return False

