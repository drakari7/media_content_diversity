import re, unicodedata
import contractions
import inflect

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import stanza

# Global pipleline, don't want to instantiate this again and again
pipeline = stanza.Pipeline(lang='hi', processors='tokenize,pos', verbose=False)

def replace_contractions(text):
    """Replace contractions in string of text"""
    return contractions.fix(text)

def remove_URL(text):
    """Remove URLs from a sample string"""
    return re.sub(r"http\S+", "", text)

def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def replace_punctuation(text):
    """Replace | with periods. Replace other punctuation with blanks"""
    text = re.sub(r'\|', r'.', text)
    return re.sub(r'[^\w\s\.]', r' ', text)

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words

def normalize_english(words):
    words = remove_non_ascii(words)
    # words = to_lowercase(words)
    words = remove_punctuation(words)
    # words = replace_numbers(words)
    # words = remove_stopwords(words)
    return words

def normalize_titles(words):
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    # words = replace_numbers(words)
    # words = remove_stopwords(words)
    return words

def clean_sample(sample):
    sample = remove_URL(sample)
    sample = replace_contractions(sample)
    sample = replace_punctuation(sample)
    return sample

def sentencing(sample):
    sample = clean_sample(sample)       # Cleaning of URLs etc
    sents = sent_tokenize(sample)       # Tokenize
    return sents

def title_nouns(sample):
    sents = sentencing(sample)
    pos_tags = []
    for sent in sents:
        words = word_tokenize(sent)
        words = normalize_titles(words)
        pos_tags.extend(pos_tag(words))
    nouns = [word.lower() for word,tag in pos_tags if tag[:2] == 'NN' and len(word) > 1]
    nouns = list(set(nouns))
    return nouns

def description_nouns(sample):
    sents = sentencing(sample)
    pos_tags = []
    for sent in sents:
        words = word_tokenize(sent)
        words = normalize_english(words)
        pos_tags.extend(pos_tag(words))
    nouns = [word.lower() for word,tag in pos_tags if tag[:2] == 'NN' and len(word) > 1]
    nouns = list(set(nouns))
    return nouns

def keyword_nouns(sample):
    sample = replace_contractions(sample)
    sample = remove_URL(sample)
    sample = re.sub(r',', r'.', sample)

    sents = sent_tokenize(sample)
    pos_tags = []
    for sent in sents:
        words = word_tokenize(sent)
        words = normalize_english(words)
        pos_tags.extend(pos_tag(words))
    nouns = [word.lower() for word,tag in pos_tags if tag[:2] == 'NN' and len(word) > 1]
    nouns = list(set(nouns))
    return nouns

# TODO: remove numbers in hindi text
#   also remove symbols like hashes etc if possible
def hi_nouns(sample):
    sample = remove_URL(sample)
    sample = re.sub(r'[A-Za-z0-9]', r' ', sample)
    sample = re.sub(r'\|', r'.', sample)
    sample = re.sub(r'\!', r'.', sample)

    doc = pipeline(sample)

    nouns = [word.text for sentence in doc.sentences for word in sentence.words
             if word.xpos[:2] == "NN" and len(word.text) > 1]
    return nouns

