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
    
def get_lcs(synset1, synset2):
    if (synset1 is not None) & (synset2 is not None):
        LCSList = synset1.lowest_common_hypernyms(synset2)
        if len(LCSList) > 0:
            return LCSList[0]
        else:
            return None
    else:
        return None

def get_synset_combos(phrase1, phrase2):
    synsets1 = wordnet.synsets(phrase1.replace(' ','_'))
    synsets2 = wordnet.synsets(phrase2.replace(' ','_'))
    comboList = []
    for syn1 in synsets1:
        for syn2 in synsets2:
            comboList.append((syn1,syn2))
    return comboList
    
def find_best_combo(comboList):
    maxSimilarity = 0
    bestCombo = None
    semcor_ic = wordnet_ic.ic('ic-semcor.dat')
    for combo in comboList:
        similarity = 0
        if(combo[0].pos() == combo[1].pos()):
            if ((combo[0].pos() != 's') & (combo[0].pos() != 'a') & (combo[0].pos() != 'r')):
                similarity = combo[0].res_similarity(combo[1], semcor_ic)
        if similarity > maxSimilarity:
            maxSimilarity = similarity
            bestCombo = combo
    return bestCombo

def get_common_concept_name(phrase1,phrase2):
    comboList = get_synset_combos(phrase1,phrase2)
    bestCombo = find_best_combo(comboList)
    if bestCombo is not None:
        commonName = get_lcs(bestCombo[0],bestCombo[1])
        return commonName.lemmas()[0].name().replace('_',' ')
    else:
        return "concept"
    # print(commonName.lemmas())
    # print(commonName.lemmas()[0].name().replace('_',' '))
    

# print(get_common_concept_name('library', 'high school'))
# print(get_common_concept_name('doctorate', 'phd'))
# print(get_common_concept_name('killer', 'criminal'))