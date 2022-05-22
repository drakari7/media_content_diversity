import matplotlib.pyplot as plt
import os
import time
import math

import tools as tl
from cat_reader import CategoryReader

## Globals 
links = tl.get_channel_links()
graph_dir = './static/graphs/'

# Fetch the dates from cache if available
dates = sorted(set(CategoryReader(links[0]).dates))
date_labels = tl.label_dates(dates)

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
            for cat, cat_w in channel.wiki_cats[idx]:
                if phrase in cat.lower():
                    w += cat_w
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
                sharey=True, figsize=(8, 12))
        cmap = plt.cm.get_cmap('hsv', n)

        idx = 0
        for idx, link in enumerate(links):
            i, j = idx//width, idx%width

            chan = CategoryReader(link)
            size = func(search_string, chan)

            axes[i, j].plot(size, c=cmap(idx))
            axes[i, j].set_title(chan.channel_name)
            axes[i, j].tick_params(labelbottom=False)

            if (i+1)*width+j >= len(links):
                a, b, c = 0, (len(dates)-1)//2, len(dates)-1
                tmp = [date_labels[a], date_labels[b], date_labels[c]]
                axes[i, j].set_xticks([a, b, c])
                axes[i, j].set_xticklabels(tmp, rotation=90)
                axes[i, j].tick_params(labelbottom=True)

        idx += 1
        # Set and rotate any empty plots also
        while idx < height*width:
            i, j = idx//width, idx%width
            fig.delaxes(axes[i, j])
            idx += 1

        fig.suptitle(f'Presence of "{search_string}" across time in Media')
        plt.tight_layout()
        plt.savefig(func_dir + search_string + '.jpg', dpi=500)

    _make_graph(get_date_weight_metadata)
    _make_graph(get_date_weight_tf_idf)

def main():
    # search_strings = ['election', 'UP', 'modi', 'kashmir', 'war', 'Pakistan', 'US', 'Ukraine', 'Belarus', 'Russia', 'kyiv', 'BJP', 'Congress', 'hindu', 'cricket', 'zelensky', 'invasion', 'chernobyl', 'ambani', 'energy', 'stock', 'lok sabha']
    # for search_string in search_strings:
    #     make_graph(search_string)

    make_graph('modi')
    pass


if __name__ == "__main__":
    main()
