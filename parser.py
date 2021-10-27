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
    title_nouns:        List[List[str]]             # Nouns in each title
    keyword_nouns:      List[List[str]]             # Nouns in content tags
    description_nouns:  List[List[str]]             # Nouns in description

    all_noun_file:      str                         # relative path to all nouns

    _all_nouns:         List[List[str]]             # other nouns combined

    def __init__(self, link):
        super().__init__(link)
        self.title_nouns = [tp.title_nouns(title) for title in self.titles]
        self.keyword_nouns = [tp.keyword_nouns(k) for k in self.content_tags]
        self.description_nouns = [tp.description_nouns(desc)
                                    for desc in self.description]

        self.all_noun_file = "nouns/all_nouns/" + self.channel_name + ".csv"
        self._all_nouns = []
        for n1, n2, n3 in zip(self.title_nouns, self.keyword_nouns,
                                self.description_nouns):
            temp = n1.copy()
            temp.extend(n2)
            temp.extend(n3)
            self._all_nouns.append(temp)

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
