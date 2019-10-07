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
    posTaggedQuery = get_pos_tagged_phrase(query)
    parseTree = get_parse_tree(posTaggedQuery)
    prettyParseTree = str(parseTree.pretty_print())
    
    # Create condition and subject arrays, populate them by traversing the parse tree, filter out stop words, and deduplicate
    conditionsAndPOS, subjectsAndPOS = [],[]
    traverse_tree(parseTree, parseTree, conditionsAndPOS, subjectsAndPOS)
    
    # stop_lexicon(conditionsAndPOS) #these directly edit the PraseAndPOS objects
    # stop_lexicon(subjectsAndPOS)
    conditionsAndPOS = deduplicate_word_list(conditionsAndPOS)
    subjectsAndPOS = deduplicate_word_list(subjectsAndPOS)
    
    # uncomment this call to see the state of PraseAndPOS Objects at any time:
    # printPraseObjState(conditionsAndPOS,subjectsAndPOS)
    
    # ConditionInfoPairings = get_most_similar_info(deduppedConditions, available_data)
    get_most_similar_info(conditionsAndPOS, available_data)

    # Generate a unique ID for the query and store it and the discovered conditions and subjects to Dynamo
    queryID = str(uuid.uuid4())
    storeQuery(table, queryID, query, parseTree, workspace)
    reducedConditionsAndPOS = storeAndDedupNewConditions(table, conditionsAndPOS, workspace, queryID) #reduced arrays are different than dedupped because they may be empty if all items were previously stored to the db
    reducedSubjectsAndPOS = storeAndDedupNewSubjects(table, subjectsAndPOS, workspace, queryID)
    
    # Build output Query to display in the console and the final JSON payload
    outputQuery = buildOutputQuery(query, conditionsAndPOS, subjectsAndPOS) 
    jsonData = package_JSON(outputQuery, reducedConditionsAndPOS, reducedSubjectsAndPOS, prettyParseTree) #use reduce conditions so that bubble aready on screen aren't added
    
    return jsonData

def printPraseObjState(conditionsAndPOS,subjectsAndPOS):
    print('Conditions:')
    for obj in conditionsAndPOS:
        print(obj.text)
        print(obj.lexType)
        print(obj.posTags)
    print('Subjects:')
    for obj in subjectsAndPOS:
        print(obj.text)
        print(obj.lexType)
        print(obj.posTags)

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

def convert_penn_to_morphy(penntag, returnNone=False):
    morphy_tag = {'NN':wordnet.NOUN, 'JJ':wordnet.ADJ,
                  'VB':wordnet.VERB, 'RB':wordnet.ADV}
    try:
        return morphy_tag[penntag[:2]]
    except:
        return None if returnNone else ''

class PhraseAndPOS:
    def __init__(self):
        self.phraseType = ''
        self.text = ''
        self.posTags = []
        self.synsets = []

def create_phrase_and_pos(phrase):
    newPhraseAndPOS = PhraseAndPOS()
    newPhraseAndPOS.text = phrase
    newPhraseAndPOS.posTags = get_pos_tagged_phrase(phrase)
    return newPhraseAndPOS

def get_pos_tagged_phrase(inputQuery):
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

def traverse_tree(tree, parent, conditionsAndPOS, subjectsAndPOS):
    # print("tree:", tree, "parent label:", parent.label())
    # if len(tree) == 1:
        # print("this is a leaf")
        # print(tree.leaves())
    if tree.label() == 'NP':
        if parent.label() == 'PP':
            # print("this is a condition")
            thisCondition = rebuild_parent_phrase(parent, conditionsAndPOS, subjectsAndPOS, 'condition')
        else:
            # print("this is a subject")
            thisSubject = rebuild_parent_phrase(tree, conditionsAndPOS, subjectsAndPOS, 'subject')
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            traverse_tree(subtree, tree, conditionsAndPOS, subjectsAndPOS)

def rebuild_parent_phrase(tree, conditionsAndPOS, subjectsAndPOS, lexType): #This function is like a "detokenizer" but for a parse tree instead of a list of words.  Replace if a better "unparser" is found
    phrase = ''
    newPhraseInstance = PhraseAndPOS()
    for leaf in tree.leaves():
        if phrase == '':
            phrase = leaf[0]
        else:
            phrase = phrase + ' ' + leaf[0]
        newPhraseInstance.posTags.append(leaf)
    newPhraseInstance.text = phrase
    newPhraseInstance.lexType = lexType
    if lexType == 'condition':
        conditionsAndPOS.append(newPhraseInstance)
    elif lexType == 'subject':
        subjectsAndPOS.append(newPhraseInstance)    
    return phrase

def stop_lexicon(lexObjects):
    for lex in lexObjects:
        stopWords = set(stopwords.words("english"))
        words = word_tokenize(lex.text)
        filteredLex = []
        for w in words:
            if w not in stopWords:
                filteredLex.append(w)
        lex.text = TreebankWordDetokenizer().detokenize(filteredLex)
        filteredLexTags = []
        for w in lex.posTags:
            if w[0] not in stopWords:
                filteredLexTags.append(w)
        lex.posTags = filteredLexTags

# def deduplicate_word_list(lexObjects):
#     foundList = []
#     for item in lexObjects:
#         if item.text in foundList:
#             lexObjects.remove(item)
#         else:    
#             foundList.append(item)
            
def deduplicate_word_list(lexObjects):
    uniqueTextList = []
    uniqueObjList = []
    for item in lexObjects:
        if item.text not in uniqueTextList:
            uniqueObjList.append(item)
            uniqueTextList.append(item.text)
    return uniqueObjList

def get_most_similar_info(lexObjects,data):
    # print('data: ' + str(data))\
    dataSynsetPacks = get_data_synset_pack(data)
    for lex in lexObjects:
        print('[LEXICON] synsets for: ' + lex.text)
        for word in lex.posTags:
            print('word: ' + word[0])
            print('Pos: ' + word[1])
            wordnetPOS = convert_penn_to_morphy(word[1])
            print('conversion: ' + str(wordnetPOS))
            synset = wordnet.synsets(word[0], wordnetPOS)
            print(str(synset))
            for syn in synset:
                print('syn (with pos): ' + str(syn))
        # for wordSynset in wordnet.synsets(word):
    
                # for dataSynset in wordnet.synsets(dataValue['text']):
                #     print('similarity of "' + str(wordSynset) + '" and "' + str(dataSynset) + '":' + str(wordSynset.wup_similarity(dataSynset)))

def get_data_synset_pack(data):
    pack = []
    for dataValue in data:
        dataPhraseAndPOS = create_phrase_and_pos(dataValue['text'])
        for word in dataPhraseAndPOS.posTags:
            dataPhraseAndPOS.synsets = get_synsets(word)
            pack.append(dataPhraseAndPOS)
    return pack

def get_synsets(wordAndTag):
    wordnetPOS = convert_penn_to_morphy(wordAndTag[1])
    synset = wordnet.synsets(wordAndTag[0], wordnetPOS)
    return synset

def buildOutputQuery(inputQuery,conditionsAndPOS,subjectsAndPOS):
    outputQuery = inputQuery

    for condition in conditionsAndPOS:
        replaceText = '{<span class=\"res-condition\">' + condition.text + '</span>}'
        outputQuery = outputQuery.replace(condition.text,replaceText)

    for subject in subjectsAndPOS:
        replaceText = '{<span class=\"res-subject\">' + subject.text + '</span>}'
        outputQuery = outputQuery.replace(subject.text,replaceText)

    return "<p>" + outputQuery + "</p>"

def package_JSON(outputQuery,reducedConditionsAndPOS,reducedSubjectsAndPOS, prettyParseTree):
    data = {}
    data['statusCode'] = '200'
    data['statusMessage'] = 'Query Parsed Successfully'
    data['version'] = "0.0.1"
    data['htmlResponse'] = outputQuery
    data['parseTree'] = prettyParseTree
    bubbles = []
    for condition in reducedConditionsAndPOS:
        bubble = {}
        bubble['internalID'] = ""
        bubble['name'] = condition.text
        bubble['type'] = "condition"
        bubble['bubbles'] = []
        bubbles.append(bubble)
    for subject in reducedSubjectsAndPOS:
        bubble = {}
        bubble['internalID'] = ""
        bubble['name'] = subject.text
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

def storeAndDedupNewSubjects(table,phraseAndPOSList, workspace, queryID):
    reducedSubjects = []
    for subject in phraseAndPOSList:
        foundItems = table.scan(
            FilterExpression=Key('text').eq(subject.text) & Key('workspace').eq(workspace) & Key('query_part').eq('subject')
        )
        if not(foundItems['Items']): #check if subject already exists
            reducedSubjects.append(subject)
            put = table.put_item(
                Item={
                    'item_id': str(uuid.uuid4()),
                    'text': subject.text,
                    'storage_source': 'parse',
                    'query_id': queryID,
                    'query_part': 'subject',
                    'create_time':str(datetime.datetime.now()),
                    'workspace': workspace,
                }
            )
    return reducedSubjects
        
def storeAndDedupNewConditions(table, phraseAndPOSList, workspace, queryID):
    reducedConditions = []
    for condition in phraseAndPOSList:
        foundItems = table.scan(
            FilterExpression=Key('text').eq(condition.text) & Key('workspace').eq(workspace) & Key('query_part').eq('condition')
        )
        if not(foundItems['Items']):
            reducedConditions.append(condition)
            put = table.put_item(
            Item={
                'item_id': str(uuid.uuid4()),
                'text': condition.text,
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