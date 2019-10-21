import numpy
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
    datafile = "sample-data/HRData_QuickSightSample.csv"
    dataset = setup_S3_source(workspace, datafile)
    
    answer, shownWork = call_query_operation(parseObject, dataset, shownWork)
    print('shown work:')
    print(shownWork)
    
    jsonData = package_JSON(workspace, answer, query, datafile, shownWork)
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
    
def call_query_operation(parseObject,dataset,shownWork):
    print(parseObject['queryType'])
    queryType = parseObject['queryType']['type']
    shownWork += showWork("Query type detected: " + queryType)
    print('shown work:')
    print(shownWork)
    if (queryType == 'count'):
        answer = count(parseObject,dataset,shownWork)
    elif (queryType == 'average'):
        answer = average(parseObject,dataset,shownWork)
    elif (queryType == 'maximum'):
        answer = maximum(parseObject,dataset,shownWork)
    elif (queryType == 'minimum'):
        answer = minimum(parseObject,dataset,shownWork)
    elif (queryType == 'summation'):
        answer = summation(parseObject,dataset,shownWork)
    elif (queryType == 'median'):
        answer = median(parseObject,dataset,shownWork)
    return answer
        
def showWork(text):
    newText = "</p><p>"
    newText += text
    print('shown work:')
    print(newText)
    return newText

def count(parseObject,df,shownWork):
    lexicon = parseObject['conditions'] + parseObject['subjects']
    for lex in lexicon:
        if (lex['closestMatchSimilarity'] > .85):
            # print('found a good enough match for filtering: ' + lex['text'] + ': ' + lex['closestMatch']['text'] + ': ' + str(lex['closestMatchSimilarity']))
            # print('length before filter = ' + str(len(df)))
            shownWork += showWork(str(lex['closestMatchSimilarity']) + " similar match found for " + lex['phraseType'] + ' ' + lex['text'] + ': ' + lex['closestMatch']['text'])
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
                shownWork += showWork("Applying filter on field " + fieldName + " for unique value: " + fieldValue + ". Length is now: " + str(len(df)))
            
        else:
            shownWork += showWork("No good matches found for " + lex['phraseType'] + ' ' + lex['text'])
            # print('this one didnt find anything decent: ' + lex['text'] + ': ' + str(lex['closestMatchSimilarity']))
    return len(df), shownWork

def average(parseObject,dataset,shownWork):
    return 2
    
def minimum(parseObject,dataset,shownWork):
    return 3

def maximum(parseObject,dataset,shownWork):
    return 4
    
def summation(parseObject,dataset,shownWork):
    return 5

def median(parseObject,dataset,shownWork):
    return 6
    
with open('test_payloads/test10-16-19.json') as f:
    data = json.load(f)
    answer(data)

