import numpy
import pandas as pd
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime

def lambda_handler(event, context):
    jsonData = answer(event['workspace'])
    return jsonData
    
def answer(workspace):
    table = setup_dynamo()
    file_name = "sample-data/HRData_QuickSightSample.csv"
    hrdata = setup_S3_source(workspace, file_name)
    
    columns = hrdata.columns
    for col in columns:
        print(col)
    
    jsonData = package_JSON(workspace)
    return jsonData

def setup_S3_source(workspace, file_name):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3') 
    obj = s3.get_object(Bucket= bucket, Key= file_name)
    return pd.read_csv(obj['Body'])

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')
    
def package_JSON(workspace):
    data = {}
    data['statusCode'] = '200'
    data['statusMessage'] = 'Answer Called Successfully'
    data['workspace'] = workspace
    return data

answer('1')

