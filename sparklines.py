import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import time
import math
import numpy as np

import tools as tl
from cat_reader import CategoryReader

## Globals 
links = tl.get_channel_links()
graph_dir = './static/graphs/'
plt.style.use('ggplot')

# Fetch the dates from cache if available
dates = sorted(set(CategoryReader(links[0]).dates))
labels = tl.label_dates(dates)

def get_date_weight_tf_idf(phrase, channel: CategoryReader):
    '''
    Get's normalised weight of phrase on given date from tfidf ranking.
    Check all videos, for the ones for which the date matches,
    search the list of tuples if the category contains the phrase.
    '''
    phrase = phrase.lower()
    ans = []
    n = len(channel.dates)

    idx = 0

    for date in dates:
        w, count = 0, 0
        while idx < n and channel.dates[idx] <= date:
            count += 1
            for noun, noun_w in channel.noun_ranks[idx].items():
                if phrase in noun:
                    w += noun_w
            idx += 1

        tmp = 0 if count == 0 else (w/count)**2 * 1000
        ans.append(tmp)
    return ans


def get_date_weight_metadata(phrase, channel: CategoryReader):
    '''
    Similar to get_date_weight_tfidf function but
    performs counting on the metadata instead.
    '''
    phrase = phrase.lower()
    ans = []
    n = len(channel.dates)

    idx = 0
    for date in dates:
        w, count = 0, 0
        while idx < n and channel.dates[idx] <= date:
            count += 1
            w += channel.titles[idx].lower().count(phrase)
            w += channel.content_tags[idx].lower().count(phrase)
            w += channel.description[idx].lower().count(phrase)
            idx += 1

        tmp = 0 if count == 0 else (w/count)**2 * 5
        ans.append(tmp)
    return ans


# Generic template concerned with plotting the graph
def make_graph(search_string):

    def _make_graph(func):
        func_dir = graph_dir + func.__name__[16:] + '/'
        os.makedirs(func_dir, exist_ok=True)

        n, width = len(links), 5
        height = math.ceil(n/width)
        fig, axes = plt.subplots(nrows=height, ncols=width,
                sharey=True, sharex=True, figsize=(8, 12))
        fig.patch.set_facecolor('lightgrey')

        idx = 0
        for idx, link in enumerate(links):
            i, j = idx//width, idx%width

            chan = CategoryReader(link)
            size = func(search_string, chan)

            axes[i, j].plot(size)
            axes[i, j].set_xlabel(tl.cutoff_cname(chan.channel_name))
            axes[i, j].tick_params(labelbottom=False)

            # if i == 0:
            #     tmp = [labels[0], labels[-1]]
            #     axes[i, j].set_xticks([0, len(labels)-1])
            #     axes[i, j].set_xticklabels(tmp, rotation=90)
            #     axes[i, j].tick_params(labeltop=True)

        idx += 1
        # Set and rotate any empty plots also
        while idx < height*width:
            i, j = idx//width, idx%width
            fig.delaxes(axes[i, j])
            idx += 1

        fig.suptitle(f"'{search_string.title()}' in News from {labels[0]} - {labels[-1]}", size='xx-large')
        plt.tight_layout()
        plt.savefig(func_dir + search_string + '.jpg', dpi=500)

    _make_graph(get_date_weight_metadata)
    # _make_graph(get_date_weight_tf_idf)

def compare_graphs(ss1, ss2):
    def _compare_graph(func):
        func_dir = graph_dir + func.__name__[16:] + '/'
        os.makedirs(func_dir, exist_ok=True)

        n, width = len(links), 5
        height = math.ceil(n/width)
        fig, axes = plt.subplots(nrows=height, ncols=width,
                sharey=True, sharex=True, figsize=(8, 12))
        fig.patch.set_facecolor('lightgrey')

        idx = 0
        for idx, link in enumerate(links):
            i, j = idx//width, idx%width

            chan = CategoryReader(link)
            size1, size2 = func(ss1, chan), func(ss2, chan)

            axes[i, j].plot(size1)
            axes[i, j].plot(size2)
            axes[i, j].set_xlabel(tl.cutoff_cname(chan.channel_name))
            axes[i, j].tick_params(labelbottom=False)

            # if i == 0:
            #     tmp = [labels[0], labels[-1]]
            #     axes[i, j].set_xticks([0, len(labels)-1])
            #     axes[i, j].set_xticklabels(tmp, rotation=90)
            #     axes[i, j].tick_params(labeltop=True)

        idx += 1
        # Set and rotate any empty plots also
        while idx < height*width:
            i, j = idx//width, idx%width
            fig.delaxes(axes[i, j])
            idx += 1

        fig.suptitle(f"'{ss1.title()}' and '{ss2.title()}' in News from {labels[0]} - {labels[-1]}", size='xx-large')
        plt.tight_layout()

        red_patch = mpatches.Patch(color='red', label=ss1)
        blue_patch = mpatches.Patch(color='blue', label=ss2)
        fig.legend(handles=[red_patch, blue_patch])

        comb_string = ss1.title() + '_' + ss2.title()
        plt.savefig(func_dir + comb_string + '.jpg', dpi=500)

    _compare_graph(get_date_weight_metadata)


def main():
    # search_strings = ['election', 'UP', 'modi', 'kashmir', 'war', 'Pakistan', 'US', 'Ukraine', 'Belarus', 'Russia', 'kyiv', 'BJP', 'Congress', 'hindu', 'cricket', 'zelensky', 'invasion', 'chernobyl', 'ambani', 'energy', 'stock', 'lok sabha']
    # for search_string in search_strings:
    #     make_graph(search_string)

    t1 = time.perf_counter()
    compare_graphs('covid', 'corona')
    # make_graph('ukraine')
    t2 = time.perf_counter()
    print(t2-t1)
    pass


if __name__ == "__main__":
    main()
