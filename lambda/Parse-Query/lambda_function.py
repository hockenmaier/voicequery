import json
import nltk
from nltk.tokenize import word_tokenize

def lambda_handler(event, context):
    
    nltk.data.path += [
    # str('home/ec2-user/environment/voicequery/lambda/Parse-Query/nltk_data')
    str('/tmp/nltk_data')
    ]
    
    # print('nltk data paths:', nltk.data.path)
    nltk.download('punkt', download_dir='/tmp/nltk_data')
    nltk.download('averaged_perceptron_tagger', download_dir='/tmp/nltk_data')
    
    # inputQuery = "How many visitors came on the lot during the upfronts"
    inputQuery = event['query']
    
    words = nltk.word_tokenize(inputQuery)
    tagged = nltk.pos_tag(words)
    # print(tagged)
    
    
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
        # print("tree:", tree, "parent label:", parent.label())
        # if len(tree) == 1:
            # print("this is a leaf")
            # print(tree.leaves())
        if tree.label() == 'NP':
            if parent.label() == 'PP':
                # print("this is a condition")
                conditions.append(getWholePhrase(parent))
            else:
                # print("this is a subject")
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
    # print("conditions:", conditions)
    # print("subjects:", subjects)
    
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
    
    # print("Input:")
    # print(inputQuery)
    # print("Output:")
    # print(outputQuery)
    
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
        return json.dumps(data)   #.replace('\/', r'/')
    
    jsonData = packageJSON(outputQuery,conditions,subjects)
    # print('JSON: ', jsonData)
    
    return {
        'statusCode': 200,
        'body': jsonData
    }
