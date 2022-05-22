import csv
import os
from threading import Thread
import time
from concurrent.futures import ThreadPoolExecutor

import text_preprocessing as tp
import tools as tl
from channel_class import NewsChannel


class EngLangProcessing(NewsChannel):
    title_nouns:        list[list[str]]             # Nouns in each title
    keyword_nouns:      list[list[str]]             # Nouns in content tags
    description_nouns:  list[list[str]]             # Nouns in description

    all_noun_dir:       str                         # Path to dir for storing
    all_noun_file:      str                         # relative path to all nouns

    _all_nouns:         list[list[str]]             # other nouns combined

    def __init__(self, link):
        super().__init__(link)
        self.title_nouns = [tp.title_nouns(title) for title in self.titles]
        self.keyword_nouns = [tp.keyword_nouns(k) for k in self.content_tags]
        self.description_nouns = [tp.description_nouns(desc)
                                    for desc in self.description]

        self.all_noun_dir = "nouns/all_nouns/"
        self.all_noun_file = self.all_noun_dir + self.channel_name + ".csv"
        self._all_nouns = []
        for n1, n2, n3 in zip(self.title_nouns, self.keyword_nouns,
                                self.description_nouns):
            temp = n1.copy()
            temp.extend(n2)
            temp.extend(n3)
            self._all_nouns.append(temp)

    # Saves all the nouns to a file
    def save_all_nouns(self):
        os.makedirs(self.all_noun_dir, exist_ok=True)
        with open(self.all_noun_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self._all_nouns)

def nlp_parse_channels(links, n_workers=6):
    def _parse_single(link):
        chan = EngLangProcessing(link)
        chan.save_all_nouns()
    
    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        ex.map(_parse_single, links)

def main():
    links = tl.get_channel_links()
    nlp_parse_channels(links)


if __name__ == "__main__":
    main()
