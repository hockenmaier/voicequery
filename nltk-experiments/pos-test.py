import nltk
from nltk.tokenize import word_tokenize

test1a = "How many visitors came on campus during upfronts?"
test1b = "How much did I spend on data storage services in Azure this year to date?"
test1c = "How well are the props purchased in the last year renting?"
test1d = "which department has the lowest revenue per square foot?"
test1e = "What was my highest utilization edit bay last month?"
test1f = "What was my AWS spend last month?"
test1g = "Which department has the highest AWS spend per user?"
test1h = "What was the most popular week to visit the lot last year?"
test1i = "Which grip assets are most often part of a subrental?"
test4 = "I shot an elephant in my pajamas"
test5 = "I closed the door"
test6 = "The door is closed"
test7 = "Do you know how to read"
test8 = "I've already read that book"
test9 = "I will walk to the store"
test10 = "Would you like to go for a walk?"

words = nltk.word_tokenize(test1a)
tagged = nltk.pos_tag(words)
print(tagged)


grammar = r"""
  NP:
    {<N.?>+}          # Chunk everything
    }<VB.?|IN>+{      # Chink sequences of VBD and IN
  """

grammar2 = r"""
  QueryType: {<W..*>+<JJ.?>?}               # Chunk "wh-words" including modifiers like "How many"
  NP: {<DT>?<PR.*>?<JJ.?>*<N.*>+}           # Chunk sequences of DT or JJ followed by one or more nouns
  PP: {<IN><NP>}                            # Chunk prepositions followed by NP
  VP: {<V.*><NP|PP|CLAUSE>+}                # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}                        # Chunk NP, VP
  """

grammar3 = r"""m
  QueryType: {<W..*>+<JJ.?>?}               # Chunk "wh-words" including modifiers like "How many"
  NP: {<DT>?<PR.*>?<JJ.?>*<N.*>+}           # Chunk sequences of DT or JJ followed by one or more nouns
  PP: {<IN><NP>}                            # Chunk prepositions followed by NP
  VP: {<V.*><NP|PP>+}                       # Chunk verbs and their arguments
  """

parser = nltk.RegexpParser(grammar2)

# for tree in parser.parse(tagged):
#         print(tree)

tree = parser.parse(tagged)
#tree.draw()

# print(tree)
# print(tree.leaves)

# for item in tree:
#   print(item)  

def traverse_tree(tree, parentLabel):
    print("tree:", tree, "parent label:", parentLabel)
    if len(tree) == 1:
      print("this is a leaf")
      #print(tree.leaves())
    if (tree.label() == 'NP') & (parentLabel == 'PP'):
      print("this is a condition")
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            traverse_tree(subtree, tree.label())

traverse_tree(tree, 'top')

tree.draw()

#Rules to write for initial voice query parsing:
# highest-level NP is a subject
# Any NP belonging to a PP is a condition


# chartGrammar = nltk.CFG.fromstring("""
# S -> NP VP
# PP -> P NP
# NP -> Det N | Det N PP | 'I'
# VP -> V NP | VP PP
# Det -> 'an' | 'my'
# N -> 'elephant' | 'pajamas'
# V -> 'shot'
# P -> 'in'
# """)

# sent = ['I', 'shot', 'an', 'elephant', 'in', 'my', 'pajamas']
# parser = nltk.ChartParser(chartGrammar)
# for tree in parser.parse(sent):
#      print(tree)


# chartGrammarReg = r"""
# S -> NP VP
# PP -> P NP
# NP -> Det N | Det N PP | 'I'
# VP -> V NP | VP PP
# Det -> 'an' | 'my'
# N -> 'elephant' | 'pajamas'
# V -> 'shot'
# P -> 'in'
# """
# #This grammar permits the sentence to be analyzed in two ways, depending on whether the prepositional phrase in my pajamas describes the elephant or the shooting event.

# sent = ['I', 'shot', 'an', 'elephant', 'in', 'my', 'pajamas']
# tagged = nltk.pos_tag(sent)
# parser = nltk.ChartParser(chartGrammarReg)
# for tree in parser.parse(tagged):
#      print(tree)
