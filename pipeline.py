import tools as tl
from data_collector import collect_all_data, append_data
from stats import views_graph, video_count_graph
from parser import nlp_parse_channels
from wiki_parser import wikiparse_channels

"""
This file will perform the entire preprocessing and pipelining process
in a sequential manner. All data processing needed to make graphs for
the website will be done here. It will import and execute different 
functions of the original files. 
This file will be run on a weekly cronjob from a server.
"""
if __name__ == "__main__":
    links = tl.get_channel_links()
    parallel_workers = 6

    # Scraping and collecting data into data/ dir
    collect_all_data(links, "1 week ago", parallel_workers)
    append_data(links)

    # Generating basic statistic graphs in graphs/ dir
    views_graph()
    video_count_graph()

    # # Perform NLP processing to generate all nouns file
    nlp_parse_channels(links, parallel_workers)

    # Do wikipedia noun filtering, and generate relevant files
    wikiparse_channels(links, parallel_workers)
