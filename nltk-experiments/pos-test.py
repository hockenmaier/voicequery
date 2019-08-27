import nltk
from nltk.tokenize import word_tokenize

testText = "How well are the props purchased in the last year renting?"

def process_content():
        words = nltk.word_tokenize(testText)
        tagged = nltk.pos_tag(words)
        print(tagged)

process_content()