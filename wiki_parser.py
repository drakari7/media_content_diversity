import mwclient
from mwclient.page import Page
from collections import Counter
import csv
import math
import time
import os
import pickle
import json
from concurrent.futures import ThreadPoolExecutor
from wordcloud import WordCloud 
import matplotlib.pyplot as plt

import tools as tl
from channel_class import NewsChannel

### Globals
site = mwclient.Site('en.wikipedia.org')

# Global cache dictionary, useful for optimising wikipedia searches
wiki_cache = {}
cache_file = tl.get_cache_dir() + "wikipedia.json"

# Wikipedia data cache funcs
def save_cache():
    with open(cache_file, "w") as f:
        json.dump(wiki_cache, f, indent=2)

def load_cache():
    with open(cache_file) as f:
        tmp = json.load(f)
    return tmp

wiki_cache = load_cache()

# Set which stores names of wiki_pages
wiki_pages: set[str]
with open(tl.get_cache_dir() + 'wiki_index.pkl', 'rb') as p:
    wiki_pages = pickle.load(p)


class WikiNounParser(NewsChannel):
    wiki_noun_file:     str                         # relative path to wiki nouns
    all_noun_file:      str                         # relative path to all nouns
    category_file:      str                         # Stores cats in pkl
    all_nouns:          list[list[str]]             # All nouns storage
    wiki_nouns:         list[list[str]]             # Filtered nouns
    wiki_cats:          list[list[tuple]]           # Common cats of videos
    cat_rank:           dict[str, float]            # Ranks of categories
    rank_coeff:         float                       # Category rank algo coeff
    freq_matrix:        list[dict[str, int]]        # Frequency count
    tf_matrix:          list[dict[str, int]]        # Term Frequency ratios
    word_per_doc_table: dict[str, int]
    idf_matrix:         list[dict[str, int]]
    # tf_idf_matrix:      list[dict[str, int]]        # was causing some errors
    video_scores:       list[float]

    tf_idf_file:        str

    def __init__(self, link):
        super().__init__(link)
        self.check_dirs()
        self.wiki_noun_file = "nouns/wiki_nouns/" + self.channel_name + ".csv"
        self.all_noun_file = "nouns/all_nouns/" + self.channel_name + ".csv"
        self.category_file = "nouns/categories/" + self.channel_name + ".pkl"
        self.tf_idf_file = "nouns/tf_idf/" + self.channel_name
        self.wordcloud_folder = "graphs/wordclouds/" + self.channel_name + "/"
        self.cat_rank = {}
        self.rank_coeff = 0.98
        self.freq_matrix = []
        self.tf_matrix = []
        self.word_per_doc_table = {}
        self.idf_matrix = []
        self.tf_idf_matrix = []
        self.video_scores = []

    # Ensures there are no stupid directory does not exist errors
    def check_dirs(self):
        os.makedirs("./nouns/wiki_nouns", exist_ok=True)
        os.makedirs("./nouns/all_nouns", exist_ok=True)
        os.makedirs("./nouns/categories", exist_ok=True)
        os.makedirs("./nouns/tf_idf", exist_ok=True)
        os.makedirs("./graphs/wordclouds", exist_ok=True)

    # Load all nouns from all noun file
    def read_all_nouns(self):
        with open(self.all_noun_file) as f:
            self.all_nouns = [text[:-1].split(',') for text in f.readlines()[:]]

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

            temp = list(set(temp))
            self.wiki_nouns.append(temp)

    def precompute_ranks(self):
        """
        Makes API calls and computes ranks of categories using inverse of
        frequency. Lowers the importance of frequent generic words which do
        not provide uniqueness to the video description.
        """
        for vid_wiki_nouns in self.wiki_nouns:
            for noun in vid_wiki_nouns:
                noun = noun.title()
                page_cats = []

                if noun in wiki_cache:  # Check if present in cache
                    page_cats = wiki_cache[noun]
                else:                   # Make an API call to wikipedia
                    page = Page(site, noun)
                    if page.exists:
                        page_cats = [p[9:] for
                                    p in page.categories(False, '!hidden')]
                    wiki_cache[noun] = page_cats

                if "Disambiguation pages" not in page_cats:
                    for cat in page_cats:
                        if cat not in self.cat_rank:
                            self.cat_rank[cat] = 1.0
                        else:
                            self.cat_rank[cat] *= self.rank_coeff


    def wiki_categoriser(self):
        """
        Calculates importance of each category by using category ranks
        computed by TFIDF scoring. This lowers the importance of
        generic pages which appear throughout multiple videos, and
        retains important pages only. Stores the important pages
        afterwards.
        """
        self.wiki_cats = []

        for vid_wiki_nouns in self.tf_idf_matrix:
            cat_counts = Counter()

            for noun, _ in vid_wiki_nouns:
                noun = noun.title()
                page_cats = wiki_cache[noun]

                if "Disambiguation pages" not in page_cats:
                    for cat in page_cats:
                        cat_counts[cat] += round(self.cat_rank[cat],3)

            self.wiki_cats.append(cat_counts.most_common(10))

    def create_frequency_matrix(self):
        for vid_wiki_nouns in self.wiki_nouns:
            freq_table = {}
            for word in vid_wiki_nouns:
                if word in freq_table:
                    freq_table[word] += 1
                else:
                    freq_table[word] = 1
            self.freq_matrix.append(freq_table)

    def create_tf_matrix(self):
        for f_table in self.freq_matrix:
            tf_table = {}
            len_sentence = len(f_table)

            for word, count in f_table.items():
                tf_table[word] = count / len_sentence

            self.tf_matrix.append(tf_table)

    def docs_per_words(self):
        for f_table in self.freq_matrix:
            for word in f_table:
                if word in self.word_per_doc_table:
                    self.word_per_doc_table[word] += 1
                else:
                    self.word_per_doc_table[word] = 1

    def create_idf_matrix(self):
        total_docs = len(self.freq_matrix)
        for f_table in self.freq_matrix:
            idf_table = {}
            for word in f_table:
                idf_table[word] = math.log10(
                            total_docs/float(self.word_per_doc_table[word])
                        )
            self.idf_matrix.append(idf_table)

    def create_tf_idf_matrix(self):
        for f_table1, f_table2 in zip(self.tf_matrix, self.idf_matrix):
            tf_idf_table = {}

            for (word1, value1), (_, value2) \
                    in zip(f_table1.items(), f_table2.items()):
                tf_idf_table[word1] = round(float(value1 * value2), 6)

            # Only taking top 10 tf idf scoring nouns
            tf_idf_table = Counter(tf_idf_table).most_common(10)
            self.tf_idf_matrix.append(tf_idf_table)


    # Wrapper function to perform tf_idf scoring
    def perform_tfidf_scoring(self):
        self.create_frequency_matrix()
        self.create_tf_matrix()
        self.docs_per_words()
        self.create_idf_matrix()
        self.create_tf_idf_matrix()

    # Wrapper func which computes category ranks
    def compute_wiki_cats(self):
        self.read_all_nouns()
        self.wiki_noun_filter()
        self.precompute_ranks()
        self.perform_tfidf_scoring()

        self.wiki_categoriser()

    def produce_wordcloud(self):
        """
        Makes wordcloud using the weights of categories calculated
        previously.
        """
        os.makedirs(self.wordcloud_folder, exist_ok=True)
        for i, vid_cats in enumerate(self.wiki_cats):
            freq_dict = {}
            for cat, weight in vid_cats:
                if  weight != 0:
                    freq_dict[cat] = weight

            img_filename = self.wordcloud_folder + str(i+1) + '.jpg'

            if freq_dict:
                vid_wcloud = WordCloud(background_color='white')
                vid_wcloud.generate_from_frequencies(freq_dict)

                plt.imshow(vid_wcloud, interpolation='bilinear')
                plt.axis('off')
                plt.savefig(img_filename)
                plt.close()
            else:       # If freq_dict is empty, save blank image
                blank_img = tl.get_blank_image()
                blank_img.save(img_filename, 'JPEG')


    # Saving categories
    def save_categories(self):
        with open(self.category_file, 'wb') as wf:
            pickle.dump(self.wiki_cats, wf)

    # Saving wiki filtered nouns
    def save_wiki_nouns(self):
        with open(self.wiki_noun_file, 'w') as wf:
            write = csv.writer(wf)
            write.writerows(self.wiki_nouns)

    def save_tf_idf_matrix(self):
        with open(self.tf_idf_file, 'w') as wf:
            for line in self.tf_idf_matrix:
                print(line, file=wf)

    # Wrapper for performing all saves in one
    def save_all(self):
        self.save_categories()
        self.save_wiki_nouns()
        self.save_tf_idf_matrix()

def wikiparse_channels(links, n_workers=6):
    def parse_single_channel(link):
        chan = WikiNounParser(link)
        chan.compute_wiki_cats()
        chan.save_all()
        # chan.produce_wordcloud()

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        executor.map(parse_single_channel, links)


def main():
    links = tl.get_channel_links()

    t1 = time.perf_counter()
    wikiparse_channels(links)

    t2 = time.perf_counter()
    print(f"time = {t2 - t1}")

    # Always save cache before exiting
    save_cache()


if __name__ == "__main__":
    main()
