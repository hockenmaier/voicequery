import json
import nltk
from nltk.tokenize import word_tokenize
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime

def lambda_handler(event, context):
    jsonData = parseQuery(event['query'])
    return jsonData
    
def parseQuery(query):
    def initial_checks():
        if (query == ""):
            data = {}
            data['statusCode'] = '422'
            data['version'] = "0.0.1"
            data['htmlResponse'] = ""
            data['parseTree'] = ""
            data['bubbles'] = []
            return False, data
        else:
            data = {}
            return True, data
    
    # print(uuid.uuid4())
    def setup_dynamo():
        dynamodb = boto3.resource('dynamodb')
        return dynamodb.Table('lexicon')
        
    
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
            replaceText = '{<span class=\"res-condition\">' + condition + '</span>}'
            outputQuery = outputQuery.replace(condition,replaceText)
    
        for subject in subjects:
            replaceText = '{<span class=\"res-subject\">' + subject + '</span>}'
            outputQuery = outputQuery.replace(subject,replaceText)
    
        return "<p>" + outputQuery + "</p>"
    
    def package_JSON(outputQuery,reducedConditions,reducedSubjects):
        data = {}
        data['statusCode'] = '200'
        data['version'] = "0.0.1"
        data['htmlResponse'] = outputQuery
        data['parseTree'] = prettyParseTree
        bubbles = []
        for condition in reducedConditions:
            bubble = {}
            bubble['internalID'] = ""
            bubble['name'] = condition
            bubble['type'] = "condition"
            bubble['bubbles'] = []
            bubbles.append(bubble)
        for subject in reducedSubjects:
            bubble = {}
            bubble['internalID'] = ""
            bubble['name'] = subject
            bubble['type'] = "subject"
            bubble['bubbles'] = []
            bubbles.append(bubble)
        data['bubbles'] = bubbles
        return data   #.replace('\/', r'/')
        
    def storeQuery(table):
        put = table.put_item(
            Item={
                'item_id': queryID,
                'text': inputQuery,
                'query_id': queryID,
                'query_part': 'query',
                'parse_tree': str(parseTree),
                'create_time': str(datetime.datetime.now()),
                'workspace': currentWorkspace,
            }
        )
        print(put)
    
    def storeAndDedupNewSubjects(table):
        reducedSubjects = subjects[:]
        for subject in subjects:
            foundItems = table.scan(
                FilterExpression=Key('text').eq(subject) & Key('workspace').eq(currentWorkspace) & Key('query_part').eq('subject')
            )
            if(foundItems['Items']): #check if subject already exists
                # print('subject to reduce:' + foundItems['Items'][0]['text'])
                reducedSubjects.remove(foundItems['Items'][0]['text'])
            else:
                put = table.put_item(
                    Item={
                        'item_id': str(uuid.uuid4()),
                        'text': subject,
                        'query_id': queryID,
                        'query_part': 'subject',
                        'create_time':str(datetime.datetime.now()),
                        'workspace': currentWorkspace,
                    }
                )
        return reducedSubjects
            
    def storeAndDedupNewConditions(table):
        reducedConditions = conditions[:]
        for condition in conditions:
            foundItems = table.scan(
                FilterExpression=Key('text').eq(condition) & Key('workspace').eq(currentWorkspace) & Key('query_part').eq('condition')
            )
            if(foundItems['Items']):
                reducedConditions.remove(foundItems['Items'][0]['text'])
            else:
                put = table.put_item(
                Item={
                    'item_id': str(uuid.uuid4()),
                    'text': condition,
                    'query_id': queryID,
                    'query_part': 'condition',
                    'create_time':str(datetime.datetime.now()),
                    'workspace': currentWorkspace,
                }
            )
        return reducedConditions
    
    checks, errData = initial_checks()
    if (checks == False):
        return errData
    currentWorkspace = '1'
    
    table = setup_dynamo()
    setup_nltk_data()
    
    inputQuery = query
    posTaggedQuery = get_pos_tagged_query()
    parseTree = get_parse_tree()
    prettyParseTree = str(parseTree.pretty_print())
    
    conditions = []
    subjects = []
    
    traverse_tree(parseTree, parseTree)
    
    queryID = str(uuid.uuid4())
    storeQuery(table)
    
    reducedConditions = storeAndDedupNewConditions(table)
    reducedSubjects = storeAndDedupNewSubjects(table)
    
    outputQuery = buildOutputQuery(inputQuery, conditions, subjects)
    jsonData = package_JSON(outputQuery, reducedConditions, reducedSubjects)
    
    return jsonData

# parseQuery("")
# parseQuery("How much wood would a woodchuck chuck if a woodchuck could chuck wood?")