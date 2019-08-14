import nltk
from nltk.tokenize import word_tokenize

testText = "What was my highest utilization edit bay last month?"

def process_content():
        words = nltk.word_tokenize(testText)
        tagged = nltk.pos_tag(words)
        print(tagged)

process_content()