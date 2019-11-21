import numpy as np
import pandas as pd
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime
import dateutil

def lambda_handler(event, context):
    # parseObject = json.loads(event)
    parseObject = event
    jsonData = answer(parseObject)
    return jsonData
    
def answer(parseObject):
    workspace = parseObject['workspace']
    query = parseObject['query']
    # table = setup_dynamo()
    sourceDataFile = "sample-data/HRData_QuickSightSample.csv"
    df = setup_S3_source(workspace, sourceDataFile)
    
    context = create_context(df,parseObject)
    
    answer = call_query_operation(context)
    # print('shown work:')
    # print(context.workToShow)
    
    jsonData = package_JSON(workspace, answer, query, sourceDataFile, context.workToShow)
    print(jsonData)
    return jsonData

class contextObject:
    def __init__(self):
        self.workToShow = ''
        self.df = None
        self.parseObject = None

def create_context(df,parseObject):
    newContext = contextObject()
    newContext.df = df
    newContext.parseObject = parseObject
    newContext.workToShow = ''
    return newContext

def setup_S3_source(workspace, file_name):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3') 
    obj = s3.get_object(Bucket= bucket, Key= file_name)
    return pd.read_csv(obj['Body'])

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')
    
def package_JSON(workspace, answer, query, datafile, workToShow):
    data = {}
    data['statusCode'] = '200'
    data['statusMessage'] = 'Answer Called Successfully'
    data['workspace'] = workspace
    data['dataFile'] = datafile
    data['query'] = query
    data['answer'] = answer
    data['workToShow'] = workToShow
    # return json.dumps(data)
    return data
    
def call_query_operation(context):
    # print(context.parseObject['queryType'])
    queryType = context.parseObject['queryType']['type']
    context.workToShow += show_work("Query type detected: " + queryType)
    # print('shown work:')
    # print(shownWork)
    if (queryType == 'count'):
        answer = count(context)
    elif (queryType == 'average'):
        answer = average(context)
    elif (queryType == 'maximum'):
        answer = maximum(context)
    elif (queryType == 'minimum'):
        answer = minimum(context)
    elif (queryType == 'summation'):
        answer = summation(context)
    elif (queryType == 'median'):
        answer = median(context)
    else:
        return 'I\'m not sure how to answer that yet'
    return answer
        
def show_work(text):
    newText = "<br>"
    newText += text
    return newText

def count(context):
    conditions,timeConditions = separate_conditions(context)
    lexicon = conditions + context.parseObject['subjects']
    filter_by_lex(context, lexicon)
    filter_by_time(context, timeConditions)
    return len(context.df)

def filter_by_lex(context, lexicon):
    for lex in lexicon:
        if (lex['closestMatchSimilarity'] > .85):
            # print('found a good enough match for filtering: ' + lex['text'] + ': ' + lex['closestMatch']['text'] + ': ' + str(lex['closestMatchSimilarity']))
            # print('length before filter = ' + str(len(df)))
            context.workToShow += show_work("Similar match (" + str(lex['closestMatchSimilarity']) + ") found for " + lex['phraseType'] + ' ' + lex['text'] + ': ' + lex['closestMatch']['text'])
            # print('shown work:')
            # print(context.workToShow)
            closestMatch = lex['closestMatch']
            if (closestMatch['phraseType'] == 'info-value'): #phrase type in the case of fields s info-field or info-value
                fieldName = closestMatch['parentFieldName']
                fieldValue = closestMatch['text']
                # print('value = ' + fieldValue)
                isValue = context.df[fieldName]==fieldValue
                context.df = context.df[isValue]
                # print('length after filter = ' + str(len(df)))
                context.workToShow += show_work("Applying filter on field " + fieldName + " for unique value: " + fieldValue + ". Number of records is now: " + str(len(context.df)))
        else:
            context.workToShow += show_work("No good matches found for " + lex['phraseType'] + ' ' + lex['text'])
            # print('this one didnt find anything decent: ' + lex['text'] + ': ' + str(lex['closestMatchSimilarity']))

def filter_by_time(context,timeConditions):
    for timeCondition in timeConditions:
        matchedDate = timeCondition['closestMatch']['text']
        if matchedDate:
            # dateValue = datetime.datetime.strptime(timeCondition['dateValue'],"%Y-%m-%d")
            dateValue = dateutil.parser.parse(timeCondition['dateValue'])
            resolution = dateValue.resolution
            print(dateValue)
            print(dateValue.year)
            print(dateValue.month)
            print(dateValue.day)
            print(datetime.datetime.now().resolution)
            matchedDateCol = pd.to_datetime(context.df[matchedDate])
            isWithinDateTime = matchedDateCol == dateValue
            context.df = context.df[isWithinDateTime]
            context.workToShow += show_work("Applying date filter on field " + matchedDate.__str__() + " for time value: " + dateValue.__str__() + ". Number of records is now: " + str(len(context.df)))

def average(context):
    chosenField = prepareForMath(context)
    if (len(context.df) == 0):
        return 'I couldn\'t do an average because no records matched the conditions in your question'
    if isinstance(chosenField, str):
        return chosenField #return String errors that were returned
    return context.df[chosenField['text']].mean()

def prepareForMath(context):
    conditions,timeConditions = separate_conditions(context)
    filter_by_lex(context,conditions) #filter by conditions
    filter_by_time(context,timeConditions)
    subjects = context.parseObject['subjects']
    numericSubs = get_numeric_lex(context,subjects)
    chosenSub,chosenField = None,None
    if numericSubs:
        for sub in numericSubs:
            if (sub['matchtype'] == 'closestMatch'):
                chosenSub = sub['sub'] #the first closestMatch numberic subject is the one we will do math on
                chosenField = sub['field']
        if not chosenSub:
            chosenSub = numericSubs[0]['sub'] #the first numberic subject is the one we will do math on if all are greatMatches
            chosenField = numericSubs[0]['field']
    else:
        return "I can't find any numeric subjects in your question to average"
    context.workToShow += show_work("The numeric subject chosen for math is: " + chosenSub['text'] + " with column: " + chosenField['text'])
    subjects.remove(chosenSub)
    filter_by_lex(context,subjects) #all other subjects than the first treated as filters
    return chosenField
    
def separate_conditions(context):
    conditions,timeConditions = [],[]
    for condition in context.parseObject['conditions']:
        if condition['phraseType'] == 'condition':
            conditions.append(condition)
        elif condition['phraseType'] == 'timeCondition':
            timeConditions.append(condition)
    print(conditions)
    print(timeConditions)
    return conditions, timeConditions

def get_numeric_lex(context,lexicon):
    numericLex = []
    print('getting numeric text')
    for lex in lexicon:
        if (lex['closestMatch']):
            print('closest match not empty')
            if (lex['closestMatch']['phraseType'] == 'info-field'): #make sure lexicon match both exists and is a field
                if np.issubdtype(context.df[lex['closestMatch']['text']].dtype, np.number): #check if column is numeric
                    context.workToShow += show_work("ClosestMatch Numeric Subject Found: " + lex['text'] + " with column: " + lex['closestMatch']['text'])
                    numericLex.append({'sub': lex, 'field': lex['closestMatch'],'matchtype': 'closestMatch'})
        if (lex['greatMatches']):
            print('greatMatches was not empty')
            for match in lex['greatMatches']:
                if (match['phraseType'] == 'info-field'): #make sure lexicon match both exists and is a field
                    print('greatMatches is a field')
                    if np.issubdtype(context.df[match['text']].dtype, np.number): #check if column is numeric
                        context.workToShow += show_work("GreatMatch Numeric Subject Found: " + lex['text'] + " with column: " + lex['closestMatch']['text'])
                        numericLex.append({'sub': lex, 'field': match,'matchtype': 'greatMatch'})
    return numericLex

def minimum(context):
    chosenField = prepareForMath(context)
    if (len(context.df) == 0):
        return 'I couldn\'t find a minimum because no records matched the conditions in your question'
    if isinstance(chosenField, str):
        return chosenField
    return context.df[chosenField['text']].min()

def maximum(context):
    chosenField = prepareForMath(context)
    if (len(context.df) == 0):
        return 'I couldn\'t find a maximum because no records matched the conditions in your question'
    if isinstance(chosenField, str):
        return chosenField
    return context.df[chosenField['text']].max()
    
def summation(context):
    chosenField = prepareForMath(context)
    if (len(context.df) == 0):
        return 'I couldn\'t add anything because no records matched the conditions in your question'
    if isinstance(chosenField, str):
        return chosenField
    return context.df[chosenField['text']].sum()

def median(context):
    chosenField = prepareForMath(context)
    if (len(context.df) == 0):
        return 'I couldn\'t find the median because no records matched the conditions in your question'
    if isinstance(chosenField, str):
        return chosenField
    return context.df[chosenField['text']].median()
    
# with open('test_payloads/test_average10-21-19.json') as f:
with open('test_payloads/test6.json') as f:
    data = json.load(f)
    answer(data)

