import mwclient
from mwclient.page import Page
from typing import List, Tuple
from collections import OrderedDict, Counter
import csv

import tools as tl
from channel_class import NewsChannel


### Globals
site = mwclient.Site('en.wikipedia.org')

# Global cache dictionary, useful for optimising wikipedia searches
wiki_cache = {}

# Set which stores names of wiki_pages
def load_wiki_pages():
    wiki_pages = set()
    multistream_path = '../wikipedia_data/multistream_index.txt'
    with open(multistream_path) as f:
        for line in f.readlines():
            page = line.split(":")[2][:-1]
            wiki_pages.add(page)

    return wiki_pages

wiki_pages = load_wiki_pages()


class WikiNounParser(NewsChannel):
    wiki_noun_file:     str                         # relative path to wiki nouns
    all_noun_file:      str                         # relative path to all nouns
    all_nouns:          List[List[str]]             # All nouns storage
    wiki_nouns:         List[List[str]]             # Filtered nouns
    wiki_cats:          List[List[Tuple]]           # Common cats of videos
    api_call_count:     int                         # No. of API calls to wiki

    def __init__(self, link):
        super().__init__(link)
        self.wiki_noun_file = "nouns/wiki_nouns/" + self.channel_name + ".csv"
        self.all_noun_file = "nouns/all_nouns/" + self.channel_name + ".csv"
        self.category_file = "nouns/categories/" + self.channel_name + ".csv"
        self.api_call_count = 0

    # Load all nouns from all noun file
    def read_all_nouns(self):
        with open(self.all_noun_file) as f:
            self.all_nouns = [text[:-1].split(',') for text in f.readlines()[:5]]

    # check if phrase exists in wikipedia (through local loaded set)
    def search_wiki(self, phrase):
        return phrase.title() in wiki_pages

    # Filter nouns based on their existence on wikipedia
    def wiki_noun_filter(self):
        self.wiki_nouns = []
        for vid_nouns in self.all_nouns:
            temp = []
            idx = 0
            while idx < len(vid_nouns)-1:
                noun = vid_nouns[idx]
                bigram = vid_nouns[idx] + ' ' + vid_nouns[idx+1]
                if self.search_wiki(bigram):
                    temp.append(bigram)
                    idx += 2
                    continue
                if self.search_wiki(noun):
                    temp.append(noun)
                idx += 1

            # Check last entry separately
            if idx==len(vid_nouns)-1 and self.search_wiki(vid_nouns[idx]):
                temp.append(vid_nouns[idx])

            temp = list(OrderedDict.fromkeys(temp))
            self.wiki_nouns.append(temp)

    # Find the most common categories for each video
    def wiki_categoriser(self):
        self.wiki_cats = []

        for vid_wiki_nouns in self.wiki_nouns:
            cat_counts = Counter()
 
            for noun in vid_wiki_nouns:
                noun = noun.title()

                if noun in wiki_cache:
                    page_cats = wiki_cache[noun]
                else:
                    page = Page(site, noun)
                    self.api_call_count += 1
                    if page.exists:
                        page_cats = [p[9:] for p in page.categories(False, '!hidden')]
                        wiki_cache[noun] = page_cats
                    else:
                        print("Page did not exist for word " + noun)
                        page_cats = []

                if "Disambiguation pages" not in page_cats:
                    cat_counts.update(page_cats)

            self.wiki_cats.append(cat_counts.most_common(10))

    # Saving categories
    def save_categories(self):
        with open(self.category_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self.wiki_cats)
        print("Saved all categories for channel :", self.channel_name)

    # Saving wiki filtered nouns
    def save_wiki_nouns(self):
        with open(self.wiki_noun_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self.wiki_nouns)
        print("Saved all wiki nouns for channel :", self.channel_name)

def main():
    links = tl.get_temp_links()

    for link in links:
        channel = WikiNounParser(link)
        channel.read_all_nouns()
        channel.wiki_noun_filter()
        # channel.save_wiki_nouns()
        channel.wiki_categoriser()
        channel.save_categories()
        print(channel.api_call_count)


if __name__ == "__main__":
    main()
