import os
import csv
import pandas as pd
from typing import List
from itertools import chain
from collections import OrderedDict

import time

import text_preprocessing as tp
import tools as tl
from channel_class import NewsChannel

# TODO:
# remove urls
# fix contractions
# correct spellings, remove URLs
# then start the POS tagging part

class LangProcessing(NewsChannel):
    wiki_data: pd.DataFrame = pd.DataFrame()        # Entire wikipedia data
    title_nouns:        List[List[str]]             # Nouns in each title
    keyword_nouns:      List[List[str]]             # Nouns in content tags
    description_nouns:  List[List[str]]             # Nouns in description
    wiki_nouns:         List[List[str]]             # Nouns appearing in wiki
    wiki_noun_file:     str                         # relative path to wiki nouns
    all_noun_file:      str                         # relative path to all nouns

    _all_nouns:         List[List[str]]             # other nouns combined

    def __init__(self, link):
        super().__init__(link)
        self.title_nouns = [tp.title_nouns(title) for title in self.titles]
        self.keyword_nouns = [tp.keyword_nouns(k) for k in self.content_tags]
        self.description_nouns = [tp.description_nouns(desc)
                                    for desc in self.description]

        self.wiki_noun_file = "nouns/wiki_nouns/" + self.channel_name + ".csv"
        self.all_noun_file = "nouns/all_nouns/" + self.channel_name + ".csv"
        self._all_nouns = []
        for n1, n2, n3 in zip(self.title_nouns, self.keyword_nouns,
                                self.description_nouns):
            temp = n1.copy()
            temp.extend(n2)
            temp.extend(n3)
            self._all_nouns.append(temp)

    # Loads wikipedia data in a pandas dataframe
    def _load_wikipedia(self):
        if not self.wiki_data.empty:
            return
        data_dir = "~/wikipedia_data/"
        heading = ['Title', 'X', 'Y']
        df = pd.read_csv(data_dir + 'meanvar1.csv', names=heading)

        for i in range(2, 58):
            file_name = data_dir + 'meanvar' + str(i) + '.csv'
            temp = pd.read_csv(file_name, names=heading)
            df = pd.concat(objs=[df, temp], ignore_index=True)  #type:ignore
        self.wiki_data = df #type:ignore

    # Search if phrase has a page on wikipedia
    def search_wiki(self, phrase) -> bool:
        return (self.wiki_data['Title'] == phrase).any()

    # check which nouns have pages on wikipedia and stores them
    def wiki_noun_checker(self):
        self._load_wikipedia()      # load wikipedia data

        self.wiki_nouns = []
        for vid_nouns in self._all_nouns:
            temp = []
            for idx in range(len(vid_nouns)-1):
                noun = vid_nouns[idx]
                bigram = vid_nouns[idx] + ' ' + vid_nouns[idx+1]
                if self.search_wiki(noun):
                    temp.append(noun)
                if self.search_wiki(bigram):
                    temp.append(bigram)

            if self.search_wiki(vid_nouns[-1]):     # check for last noun
                temp.append(vid_nouns[-1])          # separately

            self.wiki_nouns.append(temp)

    # Saves the found wikipedia nouns to a file
    def save_wiki_nouns(self):
        with open(self.wiki_noun_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self.wiki_nouns)

    # Saves all the nouns to a file
    def save_all_nouns(self):
        with open(self.all_noun_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self._all_nouns)


def main():
    links = tl.get_temp_links()

    for link in links:
        print(tl.get_channel_name(link) + ' started')
        s_time = time.perf_counter()
        channel = LangProcessing(link)
        print(f"t1 {time.perf_counter() - s_time}")
        channel.wiki_noun_checker()
        print(f"t2 {time.perf_counter() - s_time}")
        channel.save_wiki_nouns()
        e_time = time.perf_counter() - s_time
        print(f"Time for channel {channel.channel_name} is {tl.format_time(e_time)}")


if __name__ == "__main__":
    main()
