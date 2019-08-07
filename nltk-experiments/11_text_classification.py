import nltk
import random
from nltk.corpus import movie_reviews

documents = [(list(movie_reviews.words(fileid)), category)
                for category in movie_reviews.categories()
                for fileid in movie_reviews.fileids(category)]

# documents = []
# for category in movie_reviews.categories():
#     for fileid in movie_reviews.fileids(category):
#         documents.append(list(movie_reviews.words(fileid)), category)

random.shuffle(documents)

# print(documents[1])

allWords = []
for w in movie_reviews.words():
    allWords.append(w.lower())

allWords = nltk.FreqDist(allWords)

# print(allWords.most_common(15))

print(allWords["stupid"])