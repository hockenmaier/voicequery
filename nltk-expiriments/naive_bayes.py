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

print(allWords)
print(allWords.most_common()[:50])


# print(allWords["stupid"])

word_features = list(allWords.keys())[:2000]
print(list(allWords.keys())[:20])

def find_features(document):
    words = set(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features

# print(find_features(movie_reviews.words('neg/cv000_29416.txt')))

featuresets = [(find_features(rev), category) for (rev, category) in documents]

training_set = featuresets[:1900]
testing_set = featuresets[1900:]

# posterior = prior occurences x liklihood / evidence
classifier = nltk.NaiveBayesClassifier.train(training_set)
print("Naive Bayes Algorythm accuracy percentage: ", (nltk.classify.accuracy(classifier,testing_set))*100)
classifier.show_most_informative_features(15)