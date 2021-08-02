import text_preprocessing as tp
import tools as tl
from channel_class import NewsChannel

# TODO: correct spellings, remove URLs
# fix the input as much as possible
# then start the POS tagging part

class LangProcessing(NewsChannel):

    def __init__(self, link):
        super().__init__(link)
    pass


def main():
    links = tl.get_temp_links()
    
    for link in links:
        test_channel = LangProcessing(link)
        print(test_channel.channel_name)



if __name__ == "__main__":
    main()
