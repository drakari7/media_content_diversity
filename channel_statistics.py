#Importing libraries
import matplotlib as plt
import statistics

from typing import List, Dict

### local imports
import tools

class News_Channel:
    
    channel_link:           str                 #Link to the youtube channel
    channel_name:           str                 #Name of the channel
    channel_data:           List[List[str]]     #Array storing the lines of extracted channel data


    def __init__(self, link):
        self.channel_link = link
        self.channel_name = tools.get_channel_name(self.channel_link)
        channel_data_file = "channel_data/" + self.channel_name + ".csv"
        
        with open(channel_data_file,"r") as file:
            self.channel_data = [ line[:-1].split("\\#\\") for line in file.readlines() ]

    ## Returns the mean of views on the channel
    def average_views(self) -> float:
        views_arr = [line[1] for line in self.channel_data] 
        views_arr = [view.split()[0].replace(',','') for view in views_arr]
        views_arr = [int(view) for view in views_arr if tools.is_int(view)]
        return statistics.mean(views_arr)

    ## Returns the time range that the data is collected in
    def time_range(self):
        return self.channel_data[-1][2] + " to " + self.channel_data[0][2]



### For testing purposes
def main():
    test_link = 'https://www.youtube.com/c/DDIndia/videos'

    test_channel = News_Channel(test_link)


    print(test_channel.time_range())


if __name__ == "__main__":
    main()
