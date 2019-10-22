import numpy as np
import pandas as pd
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime



def lambda_handler(event, context):
    # parseObject = json.loads(event)
    parseObject = event
    jsonData = answer(parseObject)
    return jsonData
    
def answer(parseObject):
    workspace = parseObject['workspace']
    query = parseObject['query']
    shownWork = ''
    table = setup_dynamo()
    sourceDataFile = "sample-data/HRData_QuickSightSample.csv"
    df = setup_S3_source(workspace, sourceDataFile)
    
    answer, shownWork = call_query_operation(parseObject, df, shownWork)
    print('shown work:')
    print(shownWork)
    
    jsonData = package_JSON(workspace, answer, query, sourceDataFile, shownWork)
    return jsonData

def setup_S3_source(workspace, file_name):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3') 
    obj = s3.get_object(Bucket= bucket, Key= file_name)
    return pd.read_csv(obj['Body'])

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')
    
def package_JSON(workspace, answer, query, datafile, shownWork):
    data = {}
    data['statusCode'] = '200'
    data['statusMessage'] = 'Answer Called Successfully'
    data['workspace'] = workspace
    data['dataFile'] = datafile
    data['query'] = query
    data['answer'] = answer
    data['shownWork'] = shownWork
    # return json.dumps(data)
    return data
    
def call_query_operation(parseObject,df,shownWork):
    print(parseObject['queryType'])
    queryType = parseObject['queryType']['type']
    shownWork += show_work("Query type detected: " + queryType)
    print('shown work:')
    print(shownWork)
    if (queryType == 'count'):
        answer = count(parseObject,df,shownWork)
    elif (queryType == 'average'):
        answer = average(parseObject,df,shownWork)
    elif (queryType == 'maximum'):
        answer = maximum(parseObject,df,shownWork)
    elif (queryType == 'minimum'):
        answer = minimum(parseObject,df,shownWork)
    elif (queryType == 'summation'):
        answer = summation(parseObject,df,shownWork)
    elif (queryType == 'median'):
        answer = median(parseObject,df,shownWork)
    return answer, shownWork
        
def show_work(text):
    newText = "</p><p>"
    newText += text
    # print('shown work:')
    # print(newText)
    return newText

def count(parseObject,df,shownWork):
    lexicon = parseObject['conditions'] + parseObject['subjects']
    df, shownWork = filter_by_lex(df,lexicon,shownWork)
    return len(df), shownWork

def filter_by_lex(df, lexicon, shownWork):
    for lex in lexicon:
        if (lex['closestMatchSimilarity'] > .85):
            # print('found a good enough match for filtering: ' + lex['text'] + ': ' + lex['closestMatch']['text'] + ': ' + str(lex['closestMatchSimilarity']))
            # print('length before filter = ' + str(len(df)))
            shownWork += show_work(str(lex['closestMatchSimilarity']) + " similar match found for " + lex['phraseType'] + ' ' + lex['text'] + ': ' + lex['closestMatch']['text'])
            print('shown work:')
            print(shownWork)
            closestMatch = lex['closestMatch']
            if (closestMatch['phraseType'] == 'info-value'): #phrase type in the case of fields s info-field or info-value
                fieldName = closestMatch['parentFieldName']
                fieldValue = closestMatch['text']
                # print('value = ' + fieldValue)
                isValue =  df[fieldName]==fieldValue
                df = df[isValue]
                # print('length after filter = ' + str(len(df)))
                shownWork += show_work("Applying filter on field " + fieldName + " for unique value: " + fieldValue + ". Length is now: " + str(len(df)))
        else:
            shownWork += show_work("No good matches found for " + lex['phraseType'] + ' ' + lex['text'])
            # print('this one didnt find anything decent: ' + lex['text'] + ': ' + str(lex['closestMatchSimilarity']))
    return df, shownWork
    
def average(parseObject,df,shownWork):
    conditions = parseObject['conditions']
    df, shownWork = filter_by_lex(df,conditions,shownWork)
    subjects = parseObject['subjects']
    numericSubs = get_numeric_lex(df,subjects)
    if numericSubs:
        chosenSub = numericSubs[0] #the first numberic subject is the one we will do math on
    else:
        return "I can't find any numeric subjects in your question to average"
    shownWork += show_work("The numeric subject chosen for averaging math is: " + chosenSub['text'] + " with column: " + chosenSub['closestMatch']['text'])
    subjects.remove(chosenSub)
    df, shownWork = filter_by_lex(df,subjects,shownWork) #all other subjects than the first treated as filters
    return df[chosenSub['closestMatch']['text']].mean(), shownWork

def get_numeric_lex(df,lexicon):
    numericLex = []
    print('getting numeric text')
    print(str(lexicon))
    for lex in lexicon:
        print(lex['text'])
        if (lex['closestMatch']):
            print(df[lex['closestMatch']['text']].dtype)
            if np.issubdtype(df[lex['closestMatch']['text']].dtype, np.number): #check if column is numeric
                show_work("Numeric Subject Found: " + lex['text'] + " with column: " + lex['closestMatch']['text'])
                numericLex.append(lex)
    return numericLex

def minimum(parseObject,df,shownWork):
    return 3

def maximum(parseObject,df,shownWork):
    return 4
    
def summation(parseObject,df,shownWork):
    return 5

def median(parseObject,df,shownWork):
    return 6
    
with open('test_payloads/test_average10-21-19.json') as f:
    data = json.load(f)
    answer(data)

