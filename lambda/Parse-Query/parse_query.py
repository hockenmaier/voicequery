import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import wordnet
from nltk.corpus import wordnet_ic
# brown_ic = wordnet_ic.ic('ic-brown.dat')
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime
import contextlib, io
# import sys
# import os
# sys.path.append(os.path.abspath("/nltk_contrib"))

import timex_mod
# import importlib
# importlib.reload(timex_mod)

# import jsonpickle
import copy
# from nltk.internals import find_jars_within_path
# from nltk.tag.stanford import StanfordPOSTagger
# from nltk.tag.senna import SennaTagger


def lambda_handler(event, context):
    jsonData = parse_query(event, event['query'])
    return jsonData

def parse_query(parseObject, inputQuery):
    #Create initial context variables
    context = create_context(parseObject)
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
    user_concepts = get_workspace_concepts(table,workspace)
    
    print('')
    print('query: ' + query)
    
    # Apply POS tags, create parse tree using Regex grammar, and then make a pretty version
    posTaggedQuery = get_pos_tagged_phrase(query)
    parseTree = get_parse_tree(posTaggedQuery)
    prettyParseTree = prettyPrintToString(parseTree)
    # context.workToShow += show_work(prettyParseTree)
    
    # Create condition and subject arrays, populate them by traversing the parse tree, filter out stop words, and deduplicate via text match
    conditionsAndPOS, subjectsAndPOS = [],[]
    traverse_tree(parseTree, parseTree, conditionsAndPOS, subjectsAndPOS)
    stop_lexicon(conditionsAndPOS) #these directly edit the PraseAndPOS objects
    stop_lexicon(subjectsAndPOS)
    conditionsAndPOS = deduplicate_lex(conditionsAndPOS)
    subjectsAndPOS = deduplicate_lex(subjectsAndPOS)
    
    #All of the field data and field synonym data is gathered in this list first so that we don't have to keep generating them later
    dataSynsetPacks = get_data_synset_pack(available_data) 
    # print('Raw data synset packs:')
    # for pack in dataSynsetPacks:
    #     printPhraseObj(pack)
    
    # Get and set date and time variables and set them in context
    get_timex_tags(query,context)
    print(context.timeExpressionList)
    get_default_date_field(dataSynsetPacks,context)
    print('Default Date Found: ' + str(context.defaultDate))
    print('Time Expressions Found: ' + str(context.timeExpressionList))
    
    # Remove conditions that are actually time phrases and add them back in again as timeconditions
    conditionsAndPOS = deduplicate_time_conditions(conditionsAndPOS,context)
    subjectsAndPOS = deduplicate_time_conditions(subjectsAndPOS,context)
    addTimeConditions(conditionsAndPOS,context)
    
    # Detect Query Type and remove query type trigger words from lexicon:
    queryType = findAndFilterQueryTerms(query, posTaggedQuery, conditionsAndPOS,subjectsAndPOS)
    print('Query Type: ' + queryType['type'] + ', specifically: ' + queryType['term'])
    
    # Pair each condition and subject with matching concept values, if they exist
    get_matching_concept_info(conditionsAndPOS, user_concepts, dataSynsetPacks)
    get_matching_concept_info(subjectsAndPOS, user_concepts, dataSynsetPacks)
    
    # Pair each condition and subject with similar field names and values found from stored dataset info
    get_most_similar_info(conditionsAndPOS, dataSynsetPacks)
    get_most_similar_info(subjectsAndPOS, dataSynsetPacks)
    
    # uncomment this call to see the state of PraseAndPOS Objects at any time:
    print_condition_and_subject_state(conditionsAndPOS,subjectsAndPOS)
    
    # Call Answer Lambda
    answerResponse = call_answer(workspace, query, parseTree, conditionsAndPOS, subjectsAndPOS, queryType)
    answerResponse = json.loads(answerResponse)
    print('Answer Response: ' + str(answerResponse))
    print('Answer: ' + str(answerResponse['answer']))

    # Generate a unique ID for the query and store it and the discovered conditions and subjects to Dynamo
    queryID = str(uuid.uuid4())
    storeQuery(table, queryID, query, parseTree, workspace)
    reducedConditionsAndPOS = store_and_dedup_phrases(table, conditionsAndPOS, workspace, queryID, 'condition') #reduced arrays are different than dedupped because they may be empty if all items were previously stored to the db
    reducedSubjectsAndPOS = store_and_dedup_phrases(table, subjectsAndPOS, workspace, queryID, 'subject')
    
    # Build output Query to display in the console and the final JSON payload
    outputQuery = build_output_query(context, query, conditionsAndPOS, subjectsAndPOS, answerResponse)
    # print('outputQuery:' + outputQuery)
    jsonData = package_JSON(outputQuery, reducedConditionsAndPOS, reducedSubjectsAndPOS, prettyParseTree) #use reduce conditions so that bubble aready on screen aren't added
    
    return jsonData

class contextObject:
    def __init__(self):
        self.workToShow = ''
        self.parseObject = None
        self.defaultDate = None
        self.timeExpressionString = ''
        self.timeExpressionList = []
        
def create_context(parseObject):
    newContext = contextObject()
    newContext.parseObject = parseObject
    newContext.workToShow = ''
    return newContext
        
def show_work(text):
    newText = "</p><p>"
    newText += text
    return newText
        
def prettyPrintToString(parseTree):
    parseTree.pretty_print()
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        parseTree.pretty_print()
    return f.getvalue()

def print_condition_and_subject_state(conditionsAndPOS, subjectsAndPOS):
    print('')
    print('-------------------------------------Conditions-------------------------------------')
    printPhraseObjState(conditionsAndPOS)
    print('')
    print('-------------------------------------Subjects-------------------------------------')
    printPhraseObjState(subjectsAndPOS)

def printPhraseObjState(phraseAndPOSList):
    for obj in phraseAndPOSList:
        printPhraseObj(obj)

def printPhraseObj(obj):
    print('')
    if (obj.phraseType == 'condition')|(obj.phraseType == 'subject'):
        print('V------------------NEW LEXICON: ------------------V ' + obj.text)
    else:
        print('v------NEW SUB-PHRASE------v ' + obj.text)
    print('Phrase Text: ' + obj.text)
    print('Phrase Type: ' + str(obj.phraseType))
    print('POS Tags: ' + str(obj.posTags))
    print('Synsets: ' + str(obj.synsets))
    print('Closest Match Similarity: ' + str(obj.closestMatchSimilarity))
    print('Parent Lexicon Match Similarity: ' + str(obj.parentLexMatchSimilarity))
    print('Unstopped Text: ' + str(obj.unStoppedText))
    print('parentLexMatchLexSynset: ' + str(obj.parentLexMatchLexSynset))
    print('parentLexMatchDataSynset: ' + str(obj.parentLexMatchDataSynset))
    print('parentLexMatchLCS: ' + str(obj.parentLexMatchLCS))
    print('dataType: ' + str(obj.dataType))
    print('cardinalityRatio: ' + str(obj.cardinalityRatio))
    print('dateValue: ' + str(obj.dateValue))
    print('id: ' + obj.id)
    
    if obj.closestMatch:
        print('')
        print('~~~~~~~Closest Match Found~~~~~~~')
        printPhraseObj(obj.closestMatch)
    
    if obj.greatMatches:
        print('')
        print('~~~Great Matches Found~~~')
        for match in obj.greatMatches:
            printPhraseObj(match)
            
    if obj.conceptMatch:
        print('')
        print('~~~~~~~User Concept Match Found~~~~~~~')
        printPhraseObj(obj.conceptMatch)
        
    if (obj.phraseType == 'condition')|(obj.phraseType == 'subject'):
        print('^------------------END LEXICON------------------^ ' + obj.text)
    else:
        print('^------END SUB-PHRASE------^ ' + obj.text)
    

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

def get_workspace_concepts(table, workspace):
    foundItems = table.scan(
        FilterExpression=Key('workspace').eq(workspace) & Key('query_part').eq('concept')
    )
    return foundItems['Items']

def setup_nltk_data():
    #Adding temporary directory:
    nltk.data.path += [str('/tmp/nltk_data')]
    # print('nltk data paths:', nltk.data.path)
    
    #Now downloading data to temporary directory
    nltk.download('punkt', download_dir='/tmp/nltk_data')
    # nltk.download('averaged_perceptron_tagger', download_dir='/tmp/nltk_data')
    nltk.download('maxent_treebank_pos_tagger', download_dir='/tmp/nltk_data')
    nltk.download('stopwords', download_dir='/tmp/nltk_data')
    nltk.download('wordnet', download_dir='/tmp/nltk_data')
    nltk.download('wordnet_ic', download_dir='/tmp/nltk_data')

def get_timex_tags(query,context):
    tagText = timex_mod.tag(query)
    # print(tagText)
    context.timeExpressionString, context.timeExpressionList = timex_mod.ground(tagText,datetime.datetime.today())
    print("Calling Timex with tagtext " + tagText + " and ground time: " + str(datetime.datetime.today()))

def get_pos_tagged_phrase(inputQuery):
    words = nltk.word_tokenize(inputQuery)
    # return nltk.pos_tag(words) # Averaged Perceptron default tagger (struggles with adjectives)
    treebankTagger = nltk.data.load('taggers/maxent_treebank_pos_tagger/english.pickle')
    return treebankTagger.tag(words)

def get_parse_tree(posTaggedQuery):
    
    baseGrammar = r"""
      NP: {<DT>?<PR.*>?<N.*>+}                                      # Chunk sequences of DT or JJ followed by one or more nouns
      JP: {<JJ.?><NP>}                                              # Chunk adjectives followed by NP
      PP: {<IN><NP|JP>}                                             # Chunk prepositions followed by NP
      VP: {<V.*><NP|PP|JJ|CLAUSE>+}                                 # Chunk verbs and their arguments
      WP: {<W..*><VP>?<JP>?<PP>?<NP>?}                              # Chunk "wh-words" and their arguments
      CLAUSE: {<NP><VP>}                                            # Chunk NP, VP
      """
    parser = nltk.RegexpParser(baseGrammar)
    return parser.parse(posTaggedQuery)
    
    chartGrammar = nltk.CFG.fromstring("""
    
    
    """)

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
    newPhraseInstance.phraseType = lexType
    for leaf in tree.leaves():
        if (tree.label() == 'JP'):
            if (leaf[1] == 'JJ') | (leaf[1] == 'JJS'):
                phrase = appendLeaf(leaf,newPhraseInstance,phrase) #For Adjective phrases, only use the adjective words
        else:
            phrase = appendLeaf(leaf,newPhraseInstance,phrase) #for Non-Adjective phrases, use the whole phrase
    newPhraseInstance.text = phrase
    if lexType == 'condition':
        conditionsAndPOS.append(newPhraseInstance)
    elif lexType == 'subject':
        subjectsAndPOS.append(newPhraseInstance)    
    return phrase
    
def appendLeaf(leaf,phraseInstance,phrase):
    #TODO If phrase contains a hyphen here, break the posTags apart (keeping pos) but keep the phrase together
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
    maxQueryTerms = ['biggest', 'largest', 'max','maximum', 'highest']
    minQueryTerms = ['min', 'minimum', 'smallest', 'lowest']
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
        if not lex.text: #if there is nothing left after removing stop words, remove the whole lexicon
            lexObjects.remove(lex)
        lex.posTags = filteredLexTags

def deduplicate_lex(lexObjects):
    uniqueTextList = []
    uniqueObjList = []
    for item in lexObjects:
        if item.text not in uniqueTextList:
            uniqueObjList.append(item)
            uniqueTextList.append(item.text)
    return uniqueObjList
    
def deduplicate_time_conditions(lexObjects,context):
    timexTexts = []
    for value in context.timeExpressionList:
        timexTexts.append(value['text'])
    uniqueObjList = []
    for item in lexObjects:
        timeCondition = False
        for text in timexTexts:
            if item.text in text:
                timeCondition = True
        if not timeCondition:
            uniqueObjList.append(item)
    return uniqueObjList
    
def addTimeConditions(conditionsAndPOS,context):
    for timeValue in context.timeExpressionList:
        newPhraseInstance = PhraseAndPOS()
        newPhraseInstance.phraseType = 'timeCondition'
        newPhraseInstance.text = timeValue['text']
        newPhraseInstance.dateValue = timeValue['value']
        newPhraseInstance.closestMatch = context.defaultDate
        conditionsAndPOS.append(newPhraseInstance)
        
def get_default_date_field(dataSynsetPacks,context):
    defaultDate = None
    maxCardinality = 0
    for dataPack in dataSynsetPacks:
        if dataPack.phraseType == 'info-field':
            if dataPack.dataType == 'datetime':
                thisCardinality = float(dataPack.cardinalityRatio)
                if  thisCardinality > maxCardinality:
                    defaultDate = dataPack
                    maxCardinality = thisCardinality
    if defaultDate:
        context.workToShow = show_work("Found highest cardinality date field to use as default: " + str(defaultDate.text))
    context.defaultDate = defaultDate
    
def get_matching_concept_info(lex_objects,user_concepts,data_packs):
    for lex in lex_objects:
        for concept in user_concepts:
            for concept_item in concept['concept_item_detail']:
                if lex.text == concept_item['text']:
                    findAndAddDataConceptMatch(lex,concept,data_packs)
                    
def findAndAddDataConceptMatch(lex,concept,data_packs):
    data_id = ''
    for concept_item in concept['concept_item_detail']:
        if (concept_item['query_part'] == 'info-field') | (concept_item['query_part'] == 'info-value'):
            data_id = concept_item['item_id']
            # print("found data: " + data_id)
    for pack in data_packs:
        if pack.id:
            if pack.id == data_id:
                lex.conceptMatch = pack
                return

def get_most_similar_info(lexObjects,dataSynsetPacks):
    # printPhraseObjState(dataSynsetPacks)
    semcor_ic = wordnet_ic.ic('ic-semcor.dat')
    # brown_ic = wordnet_ic.ic('ic-brown.dat')
    for lex in lexObjects: #---Iterate through condition or subject phrases
        # print('[LEXICON] finding field value similarities for: ' + lex.text)
        maxSimilarity = 0
        append_phrase_and_word_synsets(lex)
        for dataPack in dataSynsetPacks: #---Iterate through each data field or value available
            # print('Comparing to: ' + dataPack.text)
            maxDataPackSimilarity = 0
            dataPacksMatched = []
            if (dataPack.text.lower() in lex.text.lower() or lex.text.lower() in dataPack.text.lower()): # If text matches exactly, we use matching length x a multiplier instead of similarity
                matchStringLenth = min(len(dataPack.text),len(lex.text))
                stringMatchSimilarity = matchStringLenth * 5
                maxSimilarity = addToMatches(dataPack,lex,stringMatchSimilarity,dataPacksMatched,maxSimilarity,None,None)
                # print('found text exactness for: ' + lex.text + ' and ' + dataPack.text)
            for lexSynList in lex.synsets: #---Iterate through each synonym set list of the lexicon at hand
                for lexSyn in lexSynList: #---Iterate through each synonym set of the lexicon at hand
                    for dataSynList in dataPack.synsets: #---Iterate through the list of data field synset lists (each list pertaining to the word in the field value, if multiple words)
                        for dataSyn in dataSynList: #---This is where we do the work.  Iterate through each data synonym and compare its similarity with the condition/subject synonym at hand
                            # print(str(dataSyn))
                            # print(str(lexSyn))
                            similarity = 0
                            if(lexSyn.pos() == dataSyn.pos()):
                                if ((lexSyn.pos() != 's') & (lexSyn.pos() != 'a') & (lexSyn.pos() != 'r')):
                                    similarity = lexSyn.res_similarity(dataSyn,semcor_ic) # This is the core similarity evaluation -------------
                            if similarity:
                                maxSimilarity = addToMatches(dataPack,lex,similarity,dataPacksMatched,maxSimilarity,dataSyn,lexSyn)
                            # if dataPack.text == 'Female':
                            #     print(str(lexSyn) + ' and ' + str(dataSyn) + ' similarity: ' + str(similarity))

def addToMatches(dataPack, lex, similarity, dataPacksMatched, maxSimilarity,dataSyn,lexSyn):
    # print(dataPacksMatched)
    isGreatMatch,isClosestMatch,isWordNetMatch = False,False,False
    if dataPack.text not in dataPacksMatched:
        if similarity > 8:
            isGreatMatch = True
    if similarity > maxSimilarity:
        isClosestMatch = True
    if dataSyn:
        isWordNetMatch = True
        
    if isClosestMatch|isGreatMatch:
        newDataPack = copy.copy(dataPack)
        newDataPack.parentLexMatchSimilarity = similarity
        if isWordNetMatch:
            lcs = get_lcs(dataSyn,lexSyn)
            newDataPack.parentLexMatchDataSynset = dataSyn
            newDataPack.parentLexMatchLexSynset = lexSyn
            newDataPack.parentLexMatchLCS = lcs
        if isGreatMatch:
            lex.greatMatches.append(newDataPack)
            dataPacksMatched.append(dataPack.text)
        if isClosestMatch:
            lex.closestMatchSimilarity = similarity
            lex.closestMatch = newDataPack
            maxSimilarity = similarity
    return maxSimilarity

def get_lcs(dataSyn,lexSyn):
    sortedHypernyms = dataSyn.lowest_common_hypernyms(lexSyn)
    # print('New Closest Match')
    # print('data Synset: ' + str(dataSyn))
    # print('lex Synset: ' + str(lexSyn))
    # print(sortedHypernyms)
    return sortedHypernyms[0]

class PhraseAndPOS:
    def __init__(self):
        self.phraseType = ''
        self.text = ''
        self.posTags = []
        self.synsets = []
        self.closestMatch = None
        self.closestMatchSimilarity = 0
        self.parentLexMatchSimilarity = 0
        self.greatMatches = []
        self.unStoppedText = ''
        self.parentFieldName = ''
        self.parentLexMatchLexSynset = None
        self.parentLexMatchDataSynset = None
        self.parentLexMatchLCS = None
        self.dataType = ''
        self.cardinalityRatio = 0
        self.dateValue = ''
        self.id = ''
        self.conceptMatch = None
    def toJSON(self):
        data = {}
        data['phraseType'] = self.phraseType
        data['text'] = self.text
        data['posTags'] = self.posTags
        data['closestMatch'] = None
        if self.closestMatch:
            data['closestMatch'] = self.closestMatch.toJSON()
        data['closestMatchSimilarity'] = self.closestMatchSimilarity
        data['parentLexMatchSimilarity'] = self.parentLexMatchSimilarity
        data['greatMatches'] = []
        for match in self.greatMatches:
            data['greatMatches'].append(match.toJSON())
        data['unStoppedText'] = self.unStoppedText
        data['parentFieldName'] = self.parentFieldName
        data['dateValue'] = self.dateValue.__str__()
        data['id'] = self.id
        data['conceptMatch'] = None
        if self.conceptMatch:
            data['conceptMatch'] = self.conceptMatch.toJSON()
        return data

def get_data_synset_pack(data):
    pack = []
    for dataValue in data:
        # print('In datavalue loop with data vaue: ' + dataValue['text'])
        dataPhraseAndPOS = create_phrase_and_pos(dataValue['text'], dataValue['query_part'])
        dataPhraseAndPOS.id = dataValue['item_id']
        if 'parent_field_name'in dataValue:
            dataPhraseAndPOS.parentFieldName = dataValue['parent_field_name']
        append_phrase_and_word_synsets(dataPhraseAndPOS)
        if dataPhraseAndPOS.phraseType == 'info-field':
            dataPhraseAndPOS.cardinalityRatio = dataValue['cardinality_ratio']
            dataPhraseAndPOS.dataType = dataValue['data_type']
        pack.append(dataPhraseAndPOS)
    return pack
    
def create_phrase_and_pos(phrase, phraseType):
    newPhraseAndPOS = PhraseAndPOS()
    newPhraseAndPOS.text = phrase
    newPhraseAndPOS.phraseType = phraseType
    newPhraseAndPOS.posTags = get_pos_tagged_phrase(phrase)
    return newPhraseAndPOS

def append_phrase_and_word_synsets(PhraseAndPOS):
    posTags = PhraseAndPOS.posTags
    if len(posTags) > 1: #get synsets for 2 or more word phrases
        for i in range(1,len(posTags)):
            phrase = posTags[i-1][0] + '_' + posTags[i][0]
            phraseSynset = []
            phraseSynset = wordnet.synsets(phrase)
            if phraseSynset:
                print('phraseSynsent: ' + str(phraseSynset))
                PhraseAndPOS.synsets.append(phraseSynset)
            else:
                # for word in PhraseAndPOS.posTags:
                #     PhraseAndPOS.synsets.append(get_synsets(word, False)) #Don't use POS to filter synsets for data fields and values
                PhraseAndPOS.synsets.append(get_synsets(posTags[i-1], False)) #The last word won't be used in any more phrases, so just add its syns if this phrase didn't match
                if(len(posTags)) == i+1:
                    PhraseAndPOS.synsets.append(get_synsets(posTags[i], False)) #if this is the last 2-word phrase and there was no phrase syns, add the second word syns
                    
    else: #just get synsets for one-word phrases
        for word in PhraseAndPOS.posTags:
            PhraseAndPOS.synsets.append(get_synsets(word, False)) #Don't use POS to filter synsets for data fields and values
        
    #todo: pair up all words and append synsets of phrases instead of words if they exist

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

def call_answer(workspace, query, parseTree, conditions, subjects, queryType):
    answerLambda = boto3.client('lambda', region_name='us-west-2')
    data = {}
    data['workspace'] = workspace
    data['query'] = query
    data['parseTree'] = parseTree
    data['conditions'] = []
    data['subjects'] = []
    for con in conditions:
        lexData = con.toJSON()
        data['conditions'].append(lexData)
        # print(jsonpickle.encode(copyCon))
    for sub in subjects:
        lexData = sub.toJSON()
        data['subjects'].append(lexData)
    #     data['conditions'].append(jsonpickle.encode(sub))
    data['queryType'] = queryType
    print('Answer Lambda Called With Payload:')
    print(json.dumps(data)) #Uncomment to see answer call payload
    answerResponse = answerLambda.invoke(FunctionName = 'Answer', InvocationType = 'RequestResponse', Payload = json.dumps(data))
    # print(str(answerResponse))
    # print(dir(answerResponse['Payload'])) #show directory of boto object
    return answerResponse['Payload'].read()

def build_output_query(context, inputQuery,conditionsAndPOS,subjectsAndPOS, answerResponse):
    outputQuery = inputQuery

    for condition in conditionsAndPOS:
        replaceText = '{<span class=\"res-condition\">' + condition.text + '</span>}'
        outputQuery = outputQuery.replace(condition.text,replaceText)

    for subject in subjectsAndPOS:
        replaceText = '{<span class=\"res-subject\">' + subject.text + '</span>}'
        outputQuery = outputQuery.replace(subject.text,replaceText)
    
    outputQuery = outputQuery + "<br>"
    outputQuery = outputQuery + context.workToShow + str(answerResponse['workToShow'])
    outputQuery = outputQuery + "</p><p>"
    outputQuery = outputQuery + "Answer: " + str(answerResponse['answer'])

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
        if condition.phraseType != 'timeCondition':
            bubble = {}
            bubble['internalID'] = condition.id
            bubble['name'] = condition.text
            bubble['type'] = condition.phraseType
            closest_match_id,closest_match_text = get_clean_closest_match(condition)
            bubble['closestMatchId'] = closest_match_id
            bubble['closestMatchText'] = closest_match_text
            bubble['bubbles'] = []
            bubbles.append(bubble)
    for subject in reducedSubjectsAndPOS:
        bubble = {}
        bubble['internalID'] = subject.id
        bubble['name'] = subject.text
        bubble['type'] = "subject"
        closest_match_id,closest_match_text = get_clean_closest_match(subject)
        bubble['closestMatchId'] = closest_match_id
        bubble['closestMatchText'] = closest_match_text
        bubble['bubbles'] = []
        bubbles.append(bubble)
    data['bubbles'] = bubbles
    return data   #.replace('\/', r'/')

def get_clean_closest_match(phrase):
    closest_match_id,closest_match_text = 'null','null'
    if phrase.closestMatch:
        closest_match_id = phrase.closestMatch.id
        closest_match_text = phrase.closestMatch.text
    return closest_match_id,closest_match_text
    
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

def store_and_dedup_phrases(table, phraseAndPOSList, workspace, queryID, lexType):
    reducedPhraseList = []
    for phrase in phraseAndPOSList:
        if phrase.phraseType != 'timeCondition':
            foundItems = table.scan(
                FilterExpression=Key('text').eq(phrase.text) & Key('workspace').eq(workspace) & Key('query_part').eq(lexType)
            )
            if not(foundItems['Items']):
                phrase.id = str(uuid.uuid4())
                reducedPhraseList.append(phrase)
                closest_match_id,closest_match_text = get_clean_closest_match(phrase)
                put = table.put_item(
                Item={
                    'item_id': phrase.id,
                    'text': phrase.text,
                    'storage_source': 'parse',
                    'query_id': queryID,
                    'query_part': lexType,
                    'create_time':str(datetime.datetime.now()),
                    'closest_match_id': closest_match_id,
                    'closest_match_text': closest_match_text,
                    'workspace': workspace,
                }
            )
    return reducedPhraseList

#-----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

# SIMPLE TESTS

# parse_query(None,"What is the median tenure for female VP's who have MS degrees?")
# parse_query(None,"How much wood would a woodchuck chuck if a woodchuck could chuck wood?")
# parse_query(None,"How many visitors came on the lot during the month of May 2019?")
# parse_query(None,"What is the average pay of our female employees with BS degrees?")
# parse_query(None,'How many engineers did we hire in 2018?')
# parse_query(None,'How many people in the operations division have their doctorates?')
# parse_query(None,'What is the average salary of people in the operations division that have their doctorates?')
# parse_query(None,'Tell me the count of female managers in the engineering organization')
# parse_query(None,'How many of the managers in engineering are women?')
# parse_query(None,'Count the number of employees with more than 10 years with the company')
# parse_query(None,'What is the average salary for employees with a BS degree?')
# parse_query(None,'What is the average tenure of female managers?')
# parse_query(None,'How many employees are male?')
# parse_query(None,'How many entry-level employees are in the engineering department?')
# parse_query(None,'what is the number of female managers in engineering that have bs degrees?')
# parse_query(None, 'What is the average salary of managers in the quality department who have MS degrees?')
# parse_query(None,'what is the average tenure of managers who are women with a high school degree?')
# parse_query(None,'what\'s the median tenure of employees in sales?')

# parse_query(None, 'What was the median revenue in the US for won opportunities?')

# TIME TESTS

# parse_query(None,'How many employees with high school education where hired before May 2012?')
# parse_query(None,'How many employees with high school education were hired in 2014')
# parse_query(None,'Last quarter, how many employees with high school education were hired?')
# parse_query(None,'How many employees with high school education were hired before this year?')
# parse_query(None,"what was the average salary of female employees last may?")


# DOUBLE TIME TEST

# parse_query(None,"how many managers were hired last april?")
# parse_query(None,"how many managers were hired last april?")

# parse_query(None,"how many managers were hired 200 weeks ago?")

#-----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#