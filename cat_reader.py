import pickle
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import tools as tl
from channel_class import NewsChannel

class CategoryReader(NewsChannel):
    category_file:      str         # Path to category file
    wiki_cats:          list[list[tuple]]
    wordcloud_folder:   str         # Folder storing wordclouds

    def __init__(self, link):
        super().__init__(link)
        self.category_file = "nouns/categories/" + self.channel_name + ".pkl"
        self.wordcloud_folder = "graphs/wordclouds/" + self.channel_name + "/"

        # read category file
        with open(self.category_file, "rb") as f:
            self.wiki_cats = pickle.load(f)

    def generate_wordcloud(self):
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

if __name__ == "__main__":
    links = tl.get_channel_links()

    for link in links[1:2]:
        chan = CategoryReader(link)
        chan.generate_wordcloud()
