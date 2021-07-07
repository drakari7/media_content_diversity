import matplotlib.pyplot as plt
import pandas as pd
import prettytable

import channel_class
import tools


graph_dir = 'graphs/'
links = tools.get_channel_links()[:10]
plt.style.use('ggplot')


def views_graph():
    views_arr = []
    channel_names = []

    for link in links:
        channel = channel_class.NewsChannel(link)
        views_arr.append(channel.average_views())
        channel_names.append(channel.channel_name)

    plt.figure()
    plt.barh(channel_names, views_arr)
    plt.xlabel('Avg no. of views')
    plt.title('Traffic at News Channels by views')
    plt.tight_layout()
    plt.savefig(graph_dir + 'views.jpg')


def video_count_graph():
    vid_counts = []
    channel_names = []

    for link in links:
        channel = channel_class.NewsChannel(link)
        vid_counts.append(channel.video_count)
        channel_names.append(channel.channel_name)

    plt.figure()
    plt.barh(channel_names, vid_counts)
    plt.xlabel('No. of videos')
    plt.title('Volume of videos by News Channels')
    plt.tight_layout()
    plt.savefig(graph_dir + 'vid_count.jpg')


def time_ranges():      #Time range in which the data has been collected
    times = []
    channel_names = []

    for link in links:
        channel = channel_class.NewsChannel(link)
        times.append(channel.time_range)
        channel_names.append(channel.channel_name)

    df = pd.DataFrame(list(zip(channel_names, times)),
                      columns=['Channel name', 'Time range'])

    table = prettytable.PrettyTable()
    table.add_column('Channel name', channel_names)
    table.add_column('Time range', times)
    print(table)


def main():
    # views_graph()
    # video_count_graph()
    time_ranges()


if __name__ == '__main__':
    main()
