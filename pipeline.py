import logging

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
    # logger options
    logging.basicConfig(filename='log_pipeline', filemode='w',
            format='%(asctime)s  %(levelname)s:%(message)s',
            level=logging.INFO,
            datefmt='%H:%M:%S')

    links = tl.get_channel_links()
    parallel_workers = 4

    logging.info(f"Starting pipeline with {parallel_workers} workers")

    # Scraping and collecting data into data/ dir
    collect_all_data(links, 1, parallel_workers)
    append_data(links)

    # Generating basic statistic graphs in graphs/ dir
    views_graph()
    video_count_graph()

    logging.info(f"Starting NLP text parsing")
    # # Perform NLP processing to generate all nouns file
    nlp_parse_channels(links, parallel_workers)

    logging.info(f"Starting wikipedia noun filtering")
    # Do wikipedia noun filtering, and generate relevant files
    wikiparse_channels(links, parallel_workers)

    logging.info("Finished pipeline")
