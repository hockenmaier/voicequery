import nltk
from nltk.tokenize import word_tokenize

test1 = "How many visitors came on campus during upfronts?"
test2 = "How much did I spend on data storage services in Azure this year to date?"
test3 = "How well are the props purchased in the last year renting?"
test4 = "I shot an elephant in my pajamas"

words = nltk.word_tokenize(test1)
tagged = nltk.pos_tag(words)
#print(tagged)


grammar = r"""
  NP:
    {<N.?>+}          # Chunk everything
    }<VB.?|IN>+{      # Chink sequences of VBD and IN
  """

grammar2 = r"""
  QueryType: {<W..*>+<JJ>?}                  # Chunk "wh-words" including modifiers like "How many"
  NP: {<DT>?<JJ>*<N.*>+}          # Chunk sequences of DT or JJ followed by one or more nouns
  PP: {<IN><NP>}               # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}           # Chunk NP, VP
  """

parser = nltk.RegexpParser(grammar2)

# for tree in parser.parse(tagged):
#         print(tree)

tree = parser.parse(tagged)
tree.draw()

chartGrammar = nltk.CFG.fromstring("""
S -> NP VP
PP -> P NP
NP -> Det N | Det N PP | 'I'
VP -> V NP | VP PP
Det -> 'an' | 'my'
N -> 'elephant' | 'pajamas'
V -> 'shot'
P -> 'in'
""")
#This grammar permits the sentence to be analyzed in two ways, depending on whether the prepositional phrase in my pajamas describes the elephant or the shooting event.

sent = ['I', 'shot', 'an', 'elephant', 'in', 'my', 'pajamas']
parser = nltk.ChartParser(chartGrammar)
for tree in parser.parse(sent):
     print(tree)