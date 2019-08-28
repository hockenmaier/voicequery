import nltk
from nltk.tokenize import word_tokenize

testText = "How many visitors came on campus during upfronts?"

words = nltk.word_tokenize(testText)
tagged = nltk.pos_tag(words)
#print(tagged)


grammar = r"""
  NP:
    {<N.?>+}          # Chunk everything
    }<VB.?|IN>+{      # Chink sequences of VBD and IN
  """

grammar2 = r"""
  NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
  PP: {<IN><NP>}               # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}           # Chunk NP, VP
  """

parser = nltk.RegexpParser(grammar2)

# for tree in parser.parse(tagged):
#         print(tree)

tree = parser.parse(tagged)
tree.draw()