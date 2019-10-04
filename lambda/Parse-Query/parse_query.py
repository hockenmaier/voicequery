import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import wordnet
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime

def lambda_handler(event, context):
    jsonData = parse_query(event['query'])
    return jsonData
    
def parse_query(query):
    
    # Perform initial checks such as ensuring the query is not an empty string
    checks, errData = initial_checks(query)
    if (checks == False):
        return errData
    workspace = '1'
    
    # Set up nltk data, dynamo connection, and get dataset values from dynamo
    table = setup_dynamo()
    setup_nltk_data()
    available_data = get_workspace_data(table,workspace)

    # Apply POS tags, create parse tree using Regex grammar, and then make a pretty version
    posTaggedQuery = get_pos_tagged_query(query)
    parseTree = get_parse_tree(posTaggedQuery)
    prettyParseTree = str(parseTree.pretty_print())
    
    # Create condition and subject arrays, populate them by traversing the parse tree, filter out stop words, and deduplicate
    conditions, subjects = [],[]
    traverse_tree(parseTree, parseTree, conditions, subjects)
    stoppedConditions = stop_lexicon(conditions)
    stoppedSubjects = stop_lexicon(subjects)
    deduppedConditions = deduplicate_word_list(stoppedConditions)
    deduppedSubjects = deduplicate_word_list(stoppedSubjects)
    
    # ConditionInfoPairings = get_most_similar_info(deduppedConditions, available_data)
    get_most_similar_info(deduppedConditions, available_data)

    # Generate a unique ID for the query and store it and the discovered conditions and subjects to Dynamo
    queryID = str(uuid.uuid4())
    storeQuery(table, queryID, query, parseTree, workspace)
    reducedConditions = storeAndDedupNewConditions(table, deduppedConditions, workspace, queryID) #reduced arrays are different than dedupped because they may be empty if all items were previously stored to the db
    reducedSubjects = storeAndDedupNewSubjects(table, deduppedSubjects, workspace, queryID)
    
    # Build output Query to display in the console and the final JSON payload
    outputQuery = buildOutputQuery(query, deduppedConditions, deduppedSubjects) 
    jsonData = package_JSON(outputQuery, reducedConditions, reducedSubjects, prettyParseTree) #use reduce conditions so that bubble aready on screen aren't added
    
    return jsonData
    
def initial_checks(query):
    if (query == ""):
        data = {}
        data['statusCode'] = '422'
        data['statusMessage'] = 'No Query Received'
        data['version'] = "0.0.1"
        data['htmlResponse'] = ""
        data['parseTree'] = ""
        data['bubbles'] = []
        return False, data
    elif (query == "."):
        setup_nltk_data()
        data = {}
        data['statusCode'] = '200'
        data['statusMessage'] = 'Lambda Boot Message Received'
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
    
def get_workspace_data(table, workspace):
    foundItems = table.scan(
        FilterExpression=Key('workspace').eq(workspace) & Key('storage_source').eq('dataset')
    )
    return foundItems['Items']
    

def setup_nltk_data():
    #Adding temporary directory:
    nltk.data.path += [str('/tmp/nltk_data')]
    # print('nltk data paths:', nltk.data.path)
    
    #Now downloading data to temporary directory
    nltk.download('punkt', download_dir='/tmp/nltk_data')
    nltk.download('averaged_perceptron_tagger', download_dir='/tmp/nltk_data')
    nltk.download('stopwords', download_dir='/tmp/nltk_data')

def get_pos_tagged_query(inputQuery):
    words = nltk.word_tokenize(inputQuery)
    return nltk.pos_tag(words)

def get_parse_tree(posTaggedQuery):
    
    baseGrammar = r"""
      QueryType: {<W..*>+<JJ.?>?}               # Chunk "wh-words" including modifiers like "How many"
      NP: {<DT>?<PR.*>?<JJ.?>*<N.*>+}           # Chunk sequences of DT or JJ followed by one or more nouns
      PP: {<IN><NP>}                            # Chunk prepositions followed by NP
      VP: {<V.*><NP|PP|CLAUSE>+}                # Chunk verbs and their arguments
      CLAUSE: {<NP><VP>}                        # Chunk NP, VP
      """
    parser = nltk.RegexpParser(baseGrammar)
    return parser.parse(posTaggedQuery)

def traverse_tree(tree, parent, conditions, subjects):
    # print("tree:", tree, "parent label:", parent.label())
    # if len(tree) == 1:
        # print("this is a leaf")
        # print(tree.leaves())
    if tree.label() == 'NP':
        if parent.label() == 'PP':
            # print("this is a condition")
            conditions.append(get_parent_phrase(parent))
        else:
            # print("this is a subject")
            subjects.append(get_parent_phrase(tree))
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            traverse_tree(subtree, tree, conditions, subjects)

def get_parent_phrase(tree): #This function is like a "detokenizer" but for a parse tree instead of a list of words.  Replace if a better "unparser" is found
    phrase = ''
    for leaf in tree.leaves():
        if phrase == '':
            phrase = leaf[0]
        else:
            phrase = phrase + ' ' + leaf[0]
    return phrase

def stop_lexicon(lexicon):
    stoppedLexicon = []
    for lex in lexicon:
        stopWords = set(stopwords.words("english"))
        words = word_tokenize(lex)
        filteredLex = []
        for w in words:
            if w not in stopWords:
                filteredLex.append(w)
        stoppedLexicon.append(TreebankWordDetokenizer().detokenize(filteredLex))
    return stoppedLexicon

def deduplicate_word_list(wordList):
    uniqueList = []
    for item in wordList:
        if item not in uniqueList:
            uniqueList.append(item)
    return uniqueList

def get_most_similar_info(wordList,data):
    # print('data: ' + str(data))\
    for word in wordList:
        print('synsets for: ' + word)
        print(str(wordnet.synsets(word)))
        # for wordSynset in wordnet.synsets(word):
    for dataValue in data:
        print('synsets for: ' + dataValue['text'])
        print(str(wordnet.synsets(dataValue['text'])))
                # for dataSynset in wordnet.synsets(dataValue['text']):
                #     print('similarity of "' + str(wordSynset) + '" and "' + str(dataSynset) + '":' + str(wordSynset.wup_similarity(dataSynset)))

def buildOutputQuery(inputQuery,stoppedConditions,stoppedSubjects):
    outputQuery = inputQuery

    for condition in stoppedConditions:
        replaceText = '{<span class=\"res-condition\">' + condition + '</span>}'
        outputQuery = outputQuery.replace(condition,replaceText)

    for subject in stoppedSubjects:
        replaceText = '{<span class=\"res-subject\">' + subject + '</span>}'
        outputQuery = outputQuery.replace(subject,replaceText)

    return "<p>" + outputQuery + "</p>"

def package_JSON(outputQuery,reducedConditions,reducedSubjects, prettyParseTree):
    data = {}
    data['statusCode'] = '200'
    data['statusMessage'] = 'Query Parsed Successfully'
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
    
def storeQuery(table, queryID, query, parseTree, workspace):
    put = table.put_item(
        Item={
            'item_id': queryID,
            'text': query,
            'storage_source': 'parse',
            'query_id': queryID,
            'query_part': 'query',
            'parse_tree': str(parseTree),
            'create_time': str(datetime.datetime.now()),
            'workspace': workspace,
        }
    )
    print(put)

def storeAndDedupNewSubjects(table,stoppedSubjects, workspace, queryID):
    reducedSubjects = stoppedSubjects[:]
    for subject in stoppedSubjects:
        foundItems = table.scan(
            FilterExpression=Key('text').eq(subject) & Key('workspace').eq(workspace) & Key('query_part').eq('subject')
        )
        if(foundItems['Items']): #check if subject already exists
            # print('subject to reduce:' + foundItems['Items'][0]['text'])
            reducedSubjects.remove(foundItems['Items'][0]['text'])
        else:
            put = table.put_item(
                Item={
                    'item_id': str(uuid.uuid4()),
                    'text': subject,
                    'storage_source': 'parse',
                    'query_id': queryID,
                    'query_part': 'subject',
                    'create_time':str(datetime.datetime.now()),
                    'workspace': workspace,
                }
            )
    return reducedSubjects
        
def storeAndDedupNewConditions(table, stoppedConditions, workspace, queryID):
    reducedConditions = stoppedConditions[:]
    for condition in stoppedConditions:
        foundItems = table.scan(
            FilterExpression=Key('text').eq(condition) & Key('workspace').eq(workspace) & Key('query_part').eq('condition')
        )
        if(foundItems['Items']):
            reducedConditions.remove(foundItems['Items'][0]['text'])
        else:
            put = table.put_item(
            Item={
                'item_id': str(uuid.uuid4()),
                'text': condition,
                'storage_source': 'parse',
                'query_id': queryID,
                'query_part': 'condition',
                'create_time':str(datetime.datetime.now()),
                'workspace': workspace,
            }
        )
    return reducedConditions

# parseQuery("")
# parse_query("How much wood would a woodchuck chuck if a woodchuck could chuck wood?")
parse_query("How many visitors came on the lot during the month of May 2019?")