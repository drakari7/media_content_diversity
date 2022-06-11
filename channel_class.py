# Importing libraries
import statistics
from datetime import timedelta, datetime

# local imports
import tools as tl


class NewsChannel:
    channel_link:   str                 # Link to the youtube channel
    channel_name:   str                 # Name of the channel
    channel_data:   list[list[str]]     # Extracted data lines
    data_file_path: str                 # relative path to the data file
    video_count:    int                 # Number of videos
    titles:         list[str]           # Titles of all the videos
    dates:          list[str]           # Array of date of video
    content_tags:   list[str]           # Keyword descriptions
    description:    list[str]           # Video descriptions
    time_range:     str                 # date range in which data was collected

    def __init__(self, link):
        self.channel_link = link
        self.channel_name = tl.get_channel_name(self.channel_link)
        self.data_file_path = "data/" + self.channel_name + ".hsv"

        with open(self.data_file_path, "r") as file:
            self.channel_data = [line[:-1].split("\\#\\")
                    for line in file.readlines()]

        self.video_count    = len(self.channel_data)
        self.titles         = [line[0] for line in self.channel_data]
        self.dates          = [line[2] for line in self.channel_data]
        self.content_tags   = [line[3] for line in self.channel_data]
        self.description    = [line[4] for line in self.channel_data]
        self.time_range     = self.dates[0] + " - " + self.dates[-1]

    # Returns the mean of views on the channel
    def average_views(self) -> float:
        views_arr = [line[1] for line in self.channel_data]
        views_arr = [view.split()[0].replace(',', '') for view in views_arr]
        views_arr = [int(view) for view in views_arr if tl.is_int(view)]
        return round(statistics.mean(views_arr), 2)

    # Checks if all lines of data are in correct format
    def is_broken(self):
        for index, line in enumerate(self.channel_data):
            if len(line) < 5:
                print(index + 1, len(line), self.channel_name)

    def missing_dates(self, start, end):
        if end < start:
            raise AssertionError("End date before start date!")

        dates = set(self.dates)
        curr = start
        missing = []
        while curr <= end:
            if curr not in dates:
                missing.append(curr)

            # Increase date by 1
            curr = datetime.strptime(curr, '%Y-%m-%d') + timedelta(1)
            curr = curr.strftime('%Y-%m-%d')

        # Print if there are any missing dates
        if missing:
            print(f"Missing dates for {self.channel_name}:")
            print(missing)



# For testing purposes
def main():
    test_links = tl.get_channel_links()

    start, end = '2022-04-23', '2022-06-09'
    for link in test_links:
        chan = NewsChannel(link)
        chan.missing_dates(start, end)



if __name__ == "__main__":
    main()
