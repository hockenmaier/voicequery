from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

ps = PorterStemmer()

exampleWords = ["python","pythoner","pythoning","pythoned","pythonly"]

newText = "It is very important to be pythonly while you are pythoning with python.  All pythoners have pythoned poorly at least once."

# for w in exampleWords:
#     print(ps.stem(w))

words = word_tokenize(newText)

for w in words:
    print(ps.stem(w))