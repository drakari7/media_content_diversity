import csv
import os
from typing import List, Set
from collections import OrderedDict
import mwclient
from mwclient.page import Page

import text_preprocessing as tp
import tools as tl
from channel_class import NewsChannel

# Global options and settings
site = mwclient.Site('en.wikipedia.org')


class EngLangProcessing(NewsChannel):
    wiki_data:          Set[str] = set()            # Entire wikipedia data
    title_nouns:        List[List[str]]             # Nouns in each title
    keyword_nouns:      List[List[str]]             # Nouns in content tags
    description_nouns:  List[List[str]]             # Nouns in description
    en_wiki_nouns:      List[List[str]]             # Nouns appearing in wiki

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

    # Loads wikipedia data in a set for O(1) lookup time
    def _load_wikipedia(self):
        if self.wiki_data:
            return

        data_dir = os.path.expanduser("~/wikipedia_data/")
        for i in range(1, 58):
            file = data_dir + "meanvar" + str(i) + ".csv"
            with open(file, 'r') as f:
                for line in f.readlines():
                    word = line.split(',')[0][1:-1]
                    self.wiki_data.add(word)

    # Search if phrase has a page on wikipedia
    def search_wiki(self, phrase) -> bool:
        page = Page(site, phrase)
        cats = [p[9:] for p in page.categories(False, '!hidden')]
        disamb = 'Disambiguation pages'

        return page.exists and disamb not in cats

    # check which nouns have pages on wikipedia and stores them
    def wiki_noun_checker(self):
        # self._load_wikipedia()      # load wikipedia data

        self.en_wiki_nouns = []
        for vid_nouns in self._all_nouns:
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
            self.en_wiki_nouns.append(temp)


    # Saves the found wikipedia nouns to a file
    def save_wiki_nouns(self):
        self.wiki_noun_checker()        # Populate wiki nouns before saving
        with open(self.wiki_noun_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self.en_wiki_nouns)
        print("Saved wiki nouns for channel :", self.channel_name)

    # Saves all the nouns to a file
    def save_all_nouns(self):
        with open(self.all_noun_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self._all_nouns)
        print("Saved all nouns for channel :", self.channel_name)

class HindiLangProcessing(EngLangProcessing):
    """This class aims to extend noun parsing to hindi text"""
    hi_title_nouns:         List[List[str]]         # title nouns for hindi
    hi_keyword_nouns:       List[List[str]]         # keyword nouns for hindi
    hi_description_nouns:   List[List[str]]         # description nouns hindi

    _hi_all_nouns:          List[List[str]]         # hindi nouns combined


    def __init__(self,link):
        super().__init__(link)
        self.hi_title_nouns = [tp.hi_nouns(title) for title in self.titles]
        self.hi_keyword_nouns = [tp.hi_nouns(k) for k in self.content_tags]
        self.hi_description_nouns = [tp.hi_nouns(desc)
                                        for desc in self.description]
        self._hi_all_nouns = []
        for n1, n2, n3 in zip(self.hi_title_nouns, self.hi_keyword_nouns,
                                self.hi_description_nouns):
            temp = n1.copy()
            temp.extend(n2)
            temp.extend(n3)
            self._hi_all_nouns.append(temp)

        for a1, a2 in zip(self._all_nouns, self._hi_all_nouns):
            a1.extend(a2)

def main():
    links = tl.get_temp_links()
    for link in links:
        channel = EngLangProcessing(link)
        count = 0

        for vid in channel._all_nouns:
            count += len(vid)

        print(count)



if __name__ == "__main__":
    main()
