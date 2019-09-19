from nltk.corpus import wordnet

syns = wordnet.synsets("program")

#synset
print(syns[0].name())

#just the word
print(syns[0].lemmas()[0].name())

#definition
print(syns[0].definition())

#examples
print(syns[0].examples())

synonyms = []
antonyms = []

for s in wordnet.synsets("good"):
    for l in s.lemmas():
        # print("l:",l)
        synonyms.append(l.name())
        if l.antonyms():
            antonyms.append(l.antonyms()[0].name())

print(set(synonyms))
print(set(antonyms))
print('/n')

w1 = wordnet.synset("ship.n.01")
w2 = wordnet.synset("boat.n.01")
print('similarity of "' + str(w1) + '" and "' + str(w2) + '":' + str(w1.wup_similarity(w2)))

w1 = wordnet.synset("ship.n.01")
w2 = wordnet.synset("car.n.01")
print('similarity of "' + str(w1) + '" and "' + str(w2) + '":' + str(w1.wup_similarity(w2)))

w1 = wordnet.synset("ship.n.01")
w2 = wordnet.synset("cactus.n.01")
print('similarity of "' + str(w1) + '" and "' + str(w2) + '":' + str(w1.wup_similarity(w2)))

w1 = wordnet.synset("visitor.n.01")
w2 = wordnet.synset("person.n.01")
print('similarity of "' + str(w1) + '" and "' + str(w2) + '":' + str(w1.wup_similarity(w2)))

w1 = wordnet.synset("visitor.n.01")
w2 = wordnet.synset("person.n.01")
print('similarity of "' + str(w1) + '" and "' + str(w2) + '":' + str(w1.wup_similarity(w2)))