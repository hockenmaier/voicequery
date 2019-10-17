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
    
    table = setup_dynamo()
    datafile = "sample-data/HRData_QuickSightSample.csv"
    dataset = setup_S3_source(workspace, datafile)
    
    answer = call_query_operation(parseObject, dataset)
    
    jsonData = package_JSON(workspace, answer, query, datafile)
    return jsonData

def setup_S3_source(workspace, file_name):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3') 
    obj = s3.get_object(Bucket= bucket, Key= file_name)
    return pd.read_csv(obj['Body'])

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')
    
def package_JSON(workspace, answer, query, datafile):
    data = {}
    data['statusCode'] = '200'
    data['statusMessage'] = 'Answer Called Successfully'
    data['workspace'] = workspace
    data['dataFile'] = datafile
    data['query'] = query
    data['answer'] = answer
    return data
    
def call_query_operation(parseObject,dataset):
    print(parseObject['queryType'])
    queryType = parseObject['queryType']['type']
    if (queryType == 'count'):
        answer = count(parseObject,dataset)
    elif (queryType == 'average'):
        answer = average(parseObject,dataset)
    elif (queryType == 'maximum'):
        answer = maximum(parseObject,dataset)
    elif (queryType == 'minimum'):
        answer = minimum(parseObject,dataset)
    elif (queryType == 'summation'):
        answer = summation(parseObject,dataset)
    elif (queryType == 'median'):
        answer = median(parseObject,dataset)
    return answer
        
def count(parseObject,dataset):
    lexicon = parseObject['conditions'] + parseObject['subjects']
    for lex in lexicon:
        if (lex['closestMatchSimilarity'] > .85):
            print('found a good enough match for filtering: ' + lex['text'] + ': ' + lex['closestMatch']['text'] + ': ' + str(lex['closestMatchSimilarity']))
        else:
            print('this one didnt find anything decent: ' + lex['text'] + ': ' + str(lex['closestMatchSimilarity']))
    return 1

def average(parseObject,dataset):
    return 2
    
def minimum(parseObject,dataset):
    return 3

def maximum(parseObject,dataset):
    return 4
    
def summation(parseObject,dataset):
    return 5

def median(parseObject,dataset):
    return 6
    
with open('test_payloads/test10-16-19.json') as f:
    data = json.load(f)
    answer(data)

