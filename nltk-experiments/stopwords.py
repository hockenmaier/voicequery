import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

sentence = "This is an example showing off stop word filtration. The kill switch is turned off right now."
# sentence = "How many visitors came on the lot last week?"

stopWords = set(stopwords.words("english"))

words = word_tokenize(sentence)

filteredSentence = []

for w in words:
    if w not in stopWords:
        filteredSentence.append(w)

# print(stopWords)
print(filteredSentence)