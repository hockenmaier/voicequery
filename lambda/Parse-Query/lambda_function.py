import json
import nltk
from nltk.tokenize import word_tokenize

def lambda_handler(event, context):
    
    def setup_nltk_data():
        #Adding temporary directory:
        nltk.data.path += [str('/tmp/nltk_data')]
        # print('nltk data paths:', nltk.data.path)
        
        #Now downloading data to temporary directory
        nltk.download('punkt', download_dir='/tmp/nltk_data')
        nltk.download('averaged_perceptron_tagger', download_dir='/tmp/nltk_data')
    
    def get_pos_tagged_query():
        words = nltk.word_tokenize(inputQuery)
        return nltk.pos_tag(words)
    
    def get_parse_tree():
        # grammar = r"""
        #   NP:
        #     {<N.?>+}          # Chunk everything
        #     }<VB.?|IN>+{      # Chink sequences of VBD and IN
        #   """
        
        baseGrammar = r"""
          QueryType: {<W..*>+<JJ.?>?}               # Chunk "wh-words" including modifiers like "How many"
          NP: {<DT>?<PR.*>?<JJ.?>*<N.*>+}           # Chunk sequences of DT or JJ followed by one or more nouns
          PP: {<IN><NP>}                            # Chunk prepositions followed by NP
          VP: {<V.*><NP|PP|CLAUSE>+}                # Chunk verbs and their arguments
          CLAUSE: {<NP><VP>}                        # Chunk NP, VP
          """
        
        # grammar3 = r"""m
        #   QueryType: {<W..*>+<JJ.?>?}               # Chunk "wh-words" including modifiers like "How many"
        #   NP: {<DT>?<PR.*>?<JJ.?>*<N.*>+}           # Chunk sequences of DT or JJ followed by one or more nouns
        #   PP: {<IN><NP>}                            # Chunk prepositions followed by NP
        #   VP: {<V.*><NP|PP>+}                       # Chunk verbs and their arguments
        #   """
        
        parser = nltk.RegexpParser(baseGrammar)
        return parser.parse(posTaggedQuery)
    
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
    
    def buildOutputQuery(inputQuery,conditions,subjects):
        outputQuery = inputQuery
    
        for condition in conditions:
            replaceText = "{<span class=\\\"res-condition\\\">" + condition + "</span>}"
            outputQuery = outputQuery.replace(condition,replaceText)
    
        for subject in subjects:
            replaceText = '{<span class=\\\"res-subject\\\">' + subject + '</span>}'
            outputQuery = outputQuery.replace(subject,replaceText)
    
        return "<p>" + outputQuery + "</p>"
    
    def package_JSON(outputQuery,conditions,subjects):
        data = {}
        data['statusCode'] = '200'
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
        return data   #.replace('\/', r'/')
    
    setup_nltk_data()
    
    inputQuery = event['query']
    posTaggedQuery = get_pos_tagged_query()
    parseTree = get_parse_tree()
    
    conditions = []
    subjects = []
    
    traverse_tree(parseTree, parseTree)
    
    outputQuery = buildOutputQuery(inputQuery,conditions,subjects)
    jsonData = package_JSON(outputQuery,conditions,subjects)
    
    return jsonData
