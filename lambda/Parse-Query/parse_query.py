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
import jsonpickle
import copy

def lambda_handler(event, context):
    jsonData = parse_query(event['query'])
    return jsonData
    
def parse_query(inputQuery):
    query = inputQuery.lower()
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
    stop_lexicon(conditionsAndPOS) #these directly edit the PraseAndPOS objects
    stop_lexicon(subjectsAndPOS)
    conditionsAndPOS = deduplicate_word_list(conditionsAndPOS)
    subjectsAndPOS = deduplicate_word_list(subjectsAndPOS)
    
    #Detect Query Type and remove query type trigger words from lexicon:
    queryType = findAndFilterQueryTerms(query, posTaggedQuery, conditionsAndPOS,subjectsAndPOS)
    print('Query Type: ' + queryType['type'] + ', specifically: ' + queryType['term'])
    
    # Pair each condition and subject with similar field names and values found from stored dataset info
    get_most_similar_info(conditionsAndPOS, available_data)
    get_most_similar_info(subjectsAndPOS, available_data)
    
    # uncomment this call to see the state of PraseAndPOS Objects at any time:
    printConditionAndSubjectState(conditionsAndPOS,subjectsAndPOS)
    
    # Call Answer Lambda
    answerResponse = callAnswer(workspace, query, parseTree, conditionsAndPOS, subjectsAndPOS, queryType)
    print(answerResponse)

    # Generate a unique ID for the query and store it and the discovered conditions and subjects to Dynamo
    queryID = str(uuid.uuid4())
    storeQuery(table, queryID, query, parseTree, workspace)
    reducedConditionsAndPOS = storeAndDedupPhrases(table, conditionsAndPOS, workspace, queryID, 'condition') #reduced arrays are different than dedupped because they may be empty if all items were previously stored to the db
    reducedSubjectsAndPOS = storeAndDedupPhrases(table, subjectsAndPOS, workspace, queryID, 'subject')
    
    # Build output Query to display in the console and the final JSON payload
    outputQuery = buildOutputQuery(query, conditionsAndPOS, subjectsAndPOS) 
    jsonData = package_JSON(outputQuery, reducedConditionsAndPOS, reducedSubjectsAndPOS, prettyParseTree) #use reduce conditions so that bubble aready on screen aren't added
    
    return jsonData

def printConditionAndSubjectState(conditionsAndPOS, subjectsAndPOS):
    print('Conditions:')
    printPhraseObjState(conditionsAndPOS)
    print('Subjects:')
    printPhraseObjState(subjectsAndPOS)

def printPhraseObjState(phraseAndPOSList):
    for obj in phraseAndPOSList:
        printPhraseObj(obj)

def printPhraseObj(obj):
    print('')
    print(obj.text)
    print(obj.phraseType)
    print(obj.posTags)
    print(obj.synsets)
    print('Closest Match Found:')
    print(obj.closestMatch)
    print(obj.closestMatchPhraseType)
    print('similarity: ' + str(obj.closestMatchSimilarity))
    print('Great Matches Found:')
    for match in obj.greatMatches:
        print(match.text)
    print(obj.unStoppedText)

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
    nltk.download('wordnet', download_dir='/tmp/nltk_data')

def get_pos_tagged_phrase(inputQuery):
    words = nltk.word_tokenize(inputQuery)
    return nltk.pos_tag(words)

def get_parse_tree(posTaggedQuery):
    
    baseGrammar = r"""
      NP: {<DT>?<PR.*>?<N.*>+}                                      # Chunk sequences of DT or JJ followed by one or more nouns
      PP: {<IN><NP>}                                                # Chunk prepositions followed by NP
      JP: {<JJ.?><NP>}                                              # Chunk adjectives followed by NP
      VP: {<V.*><NP|PP|CLAUSE>+}                                    # Chunk verbs and their arguments
      WP: {<W..*><JP>?<PP>?<NP>?}                                   # Chunk "wh-words" and their arguments
      CLAUSE: {<NP><VP>}                                            # Chunk NP, VP
      """
    parser = nltk.RegexpParser(baseGrammar)
    return parser.parse(posTaggedQuery)

def traverse_tree(tree, parent, conditionsAndPOS, subjectsAndPOS):
    if tree.label() == 'NP':
        if parent.label() == 'PP':
            thisCondition = build_lexicon_phrase(parent, conditionsAndPOS, subjectsAndPOS, 'condition')
        elif parent.label() == 'JP':
            thisCondition = build_lexicon_phrase(parent, conditionsAndPOS, subjectsAndPOS, 'condition') #We add both adjective and target noun as lexicon in the case of adjective phrases.  For the adjective portion, we remove the noun-phrase in the "build_lexicon_phrase" function
            thisSubject = build_lexicon_phrase(tree, conditionsAndPOS, subjectsAndPOS, 'subject')
        else:
            thisSubject = build_lexicon_phrase(tree, conditionsAndPOS, subjectsAndPOS, 'subject') #Noun phrases outside of other phrases are considered subjects
    elif tree.label() == 'VP':
            thisSubject = build_lexicon_phrase(tree, conditionsAndPOS, subjectsAndPOS, 'subject')
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            traverse_tree(subtree, tree, conditionsAndPOS, subjectsAndPOS)

def build_lexicon_phrase(tree, conditionsAndPOS, subjectsAndPOS, lexType): #This function is like a "detokenizer" but for a parse tree instead of a list of words.  Replace if a better "unparser" is found
    phrase = ''
    newPhraseInstance = PhraseAndPOS()
    for leaf in tree.leaves():
        if (tree.label() == 'JP'):
            if (leaf[1] == 'JJ') | (leaf[1] == 'JJS'):
                phrase = appendLeaf(leaf,newPhraseInstance,phrase) #For Adjective phrases, only use the adjective words
        else:
            phrase = appendLeaf(leaf,newPhraseInstance,phrase) #for Non-Adjective phrases, use the whole phrase
    newPhraseInstance.text = phrase
    newPhraseInstance.lexType = lexType
    if lexType == 'condition':
        conditionsAndPOS.append(newPhraseInstance)
    elif lexType == 'subject':
        subjectsAndPOS.append(newPhraseInstance)    
    return phrase
    
def appendLeaf(leaf,phraseInstance,phrase):
    if phrase == '':
        phrase = leaf[0]
    else:
        phrase = phrase + ' ' + leaf[0]
    phraseInstance.posTags.append(leaf)
    return phrase

def findAndFilterQueryTerms(query, posTaggedQuery, conditions, subjects):
    queryType = {
        'type':'Not Found',
        'term':''
        }
    
    medianQueryTerms = ['median']
    sumQueryTerms = ['add', 'sum', 'total']
    maxQueryTerms = ['biggest', 'largest', 'max','maximum']
    minQueryTerms = ['min', 'minimum', 'smallest']
    aveQueryTerms = ['mean', 'average']
    countQueryTerms = ['number','count','how many']
    allQueryTerms = medianQueryTerms + sumQueryTerms + maxQueryTerms + minQueryTerms + aveQueryTerms + countQueryTerms
    #Priority of these lists is later list higher priority, later word higher priority
    
    
    for term in medianQueryTerms:
        queryType = setQueryType(query, posTaggedQuery, queryType, term, 'median')
    for term in sumQueryTerms:
        queryType = setQueryType(query, posTaggedQuery, queryType, term, 'summation')
    for term in maxQueryTerms:
        queryType = setQueryType(query, posTaggedQuery, queryType, term, 'maximum')
    for term in minQueryTerms:
        queryType = setQueryType(query, posTaggedQuery, queryType, term, 'minimum')
    for term in aveQueryTerms:
        queryType = setQueryType(query, posTaggedQuery, queryType, term, 'average')
    for term in countQueryTerms:
        queryType = setQueryType(query, posTaggedQuery, queryType, term, 'count')
    
    
    lockedCons = conditions[:]
    lockedSubs = subjects[:]
    for condition in lockedCons:
        if (condition.text in allQueryTerms):
            conditions.remove(condition)
    for subject in lockedSubs:
        if (subject.text in allQueryTerms):
            subjects.remove(subject)
    
    return queryType
                
def setQueryType(query, posTaggedQuery, queryType, term, queryTypeText):
    wordCount = len(word_tokenize(term))
    # print('term is ' + str(term) + ' and wordCount is: ' + str(wordCount))
    if wordCount > 1:
        if term in query:
            queryType['type'] = queryTypeText
            queryType['term'] = term
            return queryType
    else:
        for posTag in posTaggedQuery:
            if term in posTag:
                queryType['type'] = queryTypeText
                queryType['term'] = term
                return queryType
    return queryType

def stop_lexicon(lexObjects):
    for lex in lexObjects:
        lex.unStoppedText = lex.text
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
    dataSynsetPacks = get_data_synset_pack(data)
    # printPhraseObjState(dataSynsetPacks)
    for lex in lexObjects: #---Iterate through condition or subject phrases
        # print('[LEXICON] finding field value similarities for: ' + lex.text)
        maxSimilarity = 0
        # closestMatch = {}
        for word in lex.posTags: #---Iterate through words in the condition or subject phrase
            lex.synsets = get_synsets(word, False)
            for lexSyn in lex.synsets: #---Iterate through each synonym of the word at hand
                for dataPack in dataSynsetPacks: #---Iterate through each data field or value available
                    # print('Comparing to: ' + dataPack.text)
                    if (dataPack.text.lower() in lex.text.lower() or lex.text.lower() in dataPack.text.lower()): # If text matches exactly, we use matching length instead of similarity
                        matchStringLenth = min(len(dataPack.text),len(lex.text))
                        if matchStringLenth > maxSimilarity:
                            lex.closestMatch = dataPack.text
                            lex.closestMatchPhraseType = dataPack.phraseType
                            lex.closestMatchSimilarity = matchStringLenth
                            maxSimilarity = matchStringLenth
                        # print('found text exactness for: ' + lex.text + ' and ' + dataPack.text)
                    for dataSynList in dataPack.synsets: #---Iterate through the list of synset lists (each list pertaining to the word in the field value, if multiple words)
                        for dataSyn in dataSynList: #---This is where we do the work.  Iterate through each data synonym and compare its similarity with the condition/subject synonym at hand
                            # print(str(dataSyn))
                            similarity = lexSyn.wup_similarity(dataSyn)
                            # if dataPack.text == 'Female':
                            #     print(str(lexSyn) + ' and ' + str(dataSyn) + ' similarity: ' + str(similarity))
                            if similarity:
                                if similarity > maxSimilarity:
                                    lex.closestMatch = dataPack.text
                                    lex.closestMatchPhraseType = dataPack.phraseType
                                    lex.closestMatchSimilarity = similarity
                                    maxSimilarity = similarity
                                if similarity > .9:
                                    if dataPack not in lex.greatMatches:
                                        lex.greatMatches.append(dataPack)

class PhraseAndPOS:
    def __init__(self):
        self.phraseType = ''
        self.text = ''
        self.posTags = []
        self.synsets = []
        self.closestMatch = ''
        self.closestMatchPhraseType = ''
        self.closestMatchSimilarity = 0
        self.greatMatches = []
        self.unStoppedText = ''
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def get_data_synset_pack(data):
    pack = []
    for dataValue in data:
        dataPhraseAndPOS = create_phrase_and_pos(dataValue['text'], dataValue['query_part'])
        for word in dataPhraseAndPOS.posTags:
            dataPhraseAndPOS.synsets.append(get_synsets(word, False)) #Don't use POS to filter synsets for data fields and values
            pack.append(dataPhraseAndPOS)
        # print('field is:' + dataValue['text'])
        # printPhraseObj(dataPhraseAndPOS)
    return pack
    
def create_phrase_and_pos(phrase, phraseType):
    newPhraseAndPOS = PhraseAndPOS()
    newPhraseAndPOS.text = phrase
    newPhraseAndPOS.posTags = get_pos_tagged_phrase(phrase)
    newPhraseAndPOS.phraseType = phraseType
    return newPhraseAndPOS

def get_synsets(wordAndTag, usePOS):
    if usePOS:
        wordnetPOS = convert_penn_to_morphy(wordAndTag[1])
        synset = wordnet.synsets(wordAndTag[0], wordnetPOS)
    else:
        synset = wordnet.synsets(wordAndTag[0])
    return synset
    
def convert_penn_to_morphy(penntag, returnNone=False):
    morphy_tag = {'NN':wordnet.NOUN, 'JJ':wordnet.ADJ,
                  'VB':wordnet.VERB, 'RB':wordnet.ADV}
    try:
        return morphy_tag[penntag[:2]]
    except:
        return None if returnNone else ''

def callAnswer(workspace, query, parseTree, conditions, subjects, queryType):
    answerLambda = boto3.client('lambda', region_name='us-west-2')
    data = {}
    data['workspace'] = workspace
    data['query'] = query
    data['parseTree'] = parseTree
    data['conditions'] = []
    data['subjects'] = []
    for con in conditions:
        copyCon = copy.copy(con)
        copyCon.posTags = []
        copyCon.synsets = []
        print('printing copy')
        printPhraseObj(copyCon)
        data['conditions'].append(jsonpickle.encode(copyCon))
        # data['conditions'].append(copyCon.toJSON())
        # print(jsonpickle.encode(copyCon))
    # for sub in subjects:
    #     data['conditions'].append(jsonpickle.encode(sub))
    data['queryType'] = queryType
    answerResponse = answerLambda.invoke(FunctionName = 'Answer', InvocationType = 'RequestResponse', Payload = json.dumps(data))
    # print(str(answerResponse))
    # print(dir(answerResponse['Payload'])) #show directory of boto object
    
    return answerResponse['Payload'].read()

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
    # print(put)

def storeAndDedupPhrases(table, phraseAndPOSList, workspace, queryID, lexType):
    reducedPhraseList = []
    for phrase in phraseAndPOSList:
        foundItems = table.scan(
            FilterExpression=Key('text').eq(phrase.text) & Key('workspace').eq(workspace) & Key('query_part').eq(lexType)
        )
        if not(foundItems['Items']):
            reducedPhraseList.append(phrase)
            put = table.put_item(
            Item={
                'item_id': str(uuid.uuid4()),
                'text': phrase.text,
                'storage_source': 'parse',
                'query_id': queryID,
                'query_part': lexType,
                'create_time':str(datetime.datetime.now()),
                'workspace': workspace,
            }
        )
    return reducedPhraseList

# parseQuery("")
# parse_query("How much wood would a woodchuck chuck if a woodchuck could chuck wood?")
# parse_query("How many visitors came on the lot during the month of May 2019?")
# parse_query("What is the average pay of our female employees with BS degrees?")
# parse_query('How many engineers did we hire in 2018?')
parse_query('How many people in the operations division have their doctorates?')
# parse_query('Tell me the count of female managers in the engineering organization')
# parse_query('How many of the managers in engineering are women?')
# parse_query('Count the number of employees with more than 10 years with the company')
# parse_query('What is the average salary for employees with a BS degree?')

