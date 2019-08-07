import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet

text = "Hello there Mr. Smith, how are ya?  The portalone is crisp and clean and python is tripping me up!  The sky is pinkish-blue.  You should not eat cardboard faster than you already are eating. Which of my wily coyotes might I bring along with me farting around town?"
text2 = "How many orders are in the latest facility deal?"
text3 = "How many people came on the lot during upfronts?"
text4 = "How many people came on the lot last week?"
text5 = "What costumes were rented the least in the last 2 years?"

# print(sent_tokenize(example_text))
# print(word_tokenize(example_text))

# for i in word_tokenize(example_text):
#     print(i)
#     print(nltk.pos_tag(i))

# for i in (nltk.pos_tag(word_tokenize(text4))):
#     print(i)

tokenized = sent_tokenize(text5, "english")

def process_content():
    try:
        for i in tokenized:
            words = nltk.word_tokenize(i)
            tagged = nltk.pos_tag(words)

            chunkGram = r"""Chunk: {<RB.?>*<VB.?>*<NN.?>+}"""

            chunkParser = nltk.RegexpParser(chunkGram)
            chunked = chunkParser.parse(tagged)
            chunked.draw()
            # print(chunked)

    except Exception as e:
        print(str(e))

process_content()

w1 = wordnet.synset("visitor.n.01")
w2 = wordnet.synset("person.n.01")
print('similarity of "' + str(w1) + '" and "' + str(w2) + '":' + str(w1.wup_similarity(w2)))