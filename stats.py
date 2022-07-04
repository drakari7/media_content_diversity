import matplotlib.pyplot as plt
import prettytable
import os

from channel_class import NewsChannel
import tools as tl


graph_dir = tl.get_root_dir() + 'graphs/'
os.makedirs(graph_dir, exist_ok=True)

links = tl.get_channel_links()
plt.style.use('ggplot')

def views_graph():
    views_arr = []
    channel_names = []

    for link in links:
        channel = NewsChannel(link)
        views_arr.append(channel.average_views())
        channel_names.append(channel.channel_name)

    plt.figure()
    plt.barh(channel_names, views_arr)
    plt.xticks(rotation=45)
    plt.title('Traffic at News Channels by views')
    plt.xlabel('Avg no. of views')
    plt.tight_layout()
    plt.savefig(graph_dir + 'views.jpg', dpi=500)


def video_count_graph():
    vid_counts = []
    channel_names = []

    for link in links:
        channel = NewsChannel(link)
        vid_counts.append(channel.video_count)
        channel_names.append(channel.channel_name)

    plt.figure()
    plt.barh(channel_names, vid_counts)
    plt.xlabel('No. of videos')
    plt.title('Volume of videos by News Channels')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(graph_dir + 'vid_count.jpg', dpi=500)


def time_ranges():      #Time range in which the data has been collected
    times = []
    channel_names = []

    for link in links:
        channel = NewsChannel(link)
        times.append(channel.time_range)
        channel_names.append(channel.channel_name)

    table = prettytable.PrettyTable()
    table.add_column('Channel name', channel_names)
    table.add_column('Time range', times)
    print(table)


def main():
    views_graph()
    video_count_graph()
    time_ranges()
    pass


if __name__ == '__main__':
    main()
