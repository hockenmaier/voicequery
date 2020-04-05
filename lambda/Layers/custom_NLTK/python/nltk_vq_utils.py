import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import wordnet
from nltk.corpus import wordnet_ic

def setup_nltk_data():
    #Adding temporary directory:
    nltk.data.path += [str('/tmp/nltk_data')]
    # print('nltk data paths:', nltk.data.path)
    
    #Now downloading data to temporary directory
    nltk.download('punkt', download_dir='/tmp/nltk_data')
    # nltk.download('averaged_perceptron_tagger', download_dir='/tmp/nltk_data')
    nltk.download('maxent_treebank_pos_tagger', download_dir='/tmp/nltk_data')
    nltk.download('stopwords', download_dir='/tmp/nltk_data')
    nltk.download('wordnet', download_dir='/tmp/nltk_data')
    nltk.download('wordnet_ic', download_dir='/tmp/nltk_data')
    
def getLCS(synset1, synset2):
    if (synset1 is not None) & (synset2 is not None):
        LCSList = synset1.lowest_common_hypernyms(synset2)
        if len(LCSList) > 0:
            return LCSList[0]
        else:
            return None
    else:
        return None