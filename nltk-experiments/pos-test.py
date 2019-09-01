import nltk
from nltk.tokenize import word_tokenize
import json

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
kaitlintest = "How many keys are there on a computer keyboard?"

inputQuery = kaitlintest

words = nltk.word_tokenize(inputQuery)
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
# tree.draw()

# print(tree)
# print(tree.leaves)

# for item in tree:
#   print(item)  

conditions = []
subjects = []

def traverse_tree(tree, parent):
    print("tree:", tree, "parent label:", parent.label())
    if len(tree) == 1:
        print("this is a leaf")
        #print(tree.leaves())
    if tree.label() == 'NP':
        if parent.label() == 'PP':
            print("this is a condition")
            conditions.append(getWholePhrase(parent))
        else:
            print("this is a subject")
            subjects.append(getWholePhrase(tree))
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            traverse_tree(subtree, tree)

def getWholePhrase(tree):
    phrase = ''
    for leaf in tree.leaves():
        if phrase == '':
            phrase = leaf[0]
        else:
            phrase = phrase + ' ' + leaf[0]
    return phrase

traverse_tree(tree, tree)
print("conditions:", conditions)
print("subjects:", subjects)

def buildOutputQuery(inputQuery,conditions,subjects):
    outputQuery = inputQuery

    for condition in conditions:
        replaceText = "{<span class=\\\"res-condition\\\">" + condition + "</span>}"
        outputQuery = outputQuery.replace(condition,replaceText)

    for subject in subjects:
        replaceText = '{<span class=\\\"res-subject\\\">' + subject + '</span>}'
        outputQuery = outputQuery.replace(subject,replaceText)

    return "<p>" + outputQuery + "</p>"

outputQuery = buildOutputQuery(inputQuery,conditions,subjects)

print("Input:")
print(inputQuery)
print("Output:")
print(outputQuery)

def packageJSON(outputQuery,conditions,subjects):
    data = {}
    data['version'] = "0.0.1"
    data['htmlResponse'] = outputQuery
    bubbles = []
    for condition in conditions:
        bubble = {}
        bubble['internalID'] = ""
        bubble['name'] = condition
        bubble['type'] = "condition"
        bubble['bubbles'] = []
        bubbles.append(bubble)
    for subject in subjects:
        bubble = {}
        bubble['internalID'] = ""
        bubble['name'] = subject
        bubble['type'] = "subject"
        bubble['bubbles'] = []
        bubbles.append(bubble)
    data['bubbles'] = bubbles
    return json.dumps(data)

jsonData = packageJSON(outputQuery,conditions,subjects)
print('JSON: ', jsonData)

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
