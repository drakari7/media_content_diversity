import pickle

import tools as tl
from channel_class import NewsChannel

class CategoryReader(NewsChannel):
    category_file:      str         # Path to category file
    wiki_cats:          list[list[tuple]]

    def __init__(self, link):
        super().__init__(link)
        self.category_file = "nouns/categories/" + self.channel_name + ".pkl"

        # read category file
        with open(self.category_file, "rb") as f:
            self.wiki_cats = pickle.load(f)
