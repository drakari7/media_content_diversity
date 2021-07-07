# Importing libraries
import statistics
# import traceback

from typing import List

# local imports
import tools


class NewsChannel:
    channel_link:   str                 # Link to the youtube channel
    channel_name:   str                 # Name of the channel
    channel_data:   List[List[str]]     # Extracted data lines
    video_count:    int                 # Number of videos
    content_tags:   List[str]           # Keyword descriptions
    time_range:     str                 # Range in which data was collected
    descriptions:   List[str]           # Video descriptions

    def __init__(self, link):
        self.channel_link = link
        self.channel_name = tools.get_channel_name(self.channel_link)
        channel_data_file = "channel_data/" + self.channel_name + ".csv"

        with open(channel_data_file, "r") as file:
            self.channel_data = [line[:-1].split("\\#\\")
                                 for line in file.readlines()]

        self.video_count = len(self.channel_data)
        self.content_tags = [line[3] for line in self.channel_data]
        self.descriptions = [line[4] for line in self.channel_data]
        self.time_range = self.channel_data[-1][2]\
                          + " - " + self.channel_data[0][2]

    # Returns the mean of views on the channel
    def average_views(self) -> float:
        views_arr = [line[1] for line in self.channel_data]
        views_arr = [view.split()[0].replace(',', '') for view in views_arr]
        views_arr = [int(view) for view in views_arr if tools.is_int(view)]
        return round(statistics.mean(views_arr), 2)

    # Checks if all lines of data are in correct format
    def is_broken(self):
        for index, line in enumerate(self.channel_data):
            if len(line) < 5:
                print(index + 1, len(line))


# For testing purposes
def main():
    test_links = tools.get_channel_links()[:10]

    for link in test_links:
        test_channel = NewsChannel(link)
        print(test_channel.video_count)


if __name__ == "__main__":
    main()
