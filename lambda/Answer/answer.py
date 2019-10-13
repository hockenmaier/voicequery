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
    unique_value_limit = 15
    hrdata = setup_S3_source(workspace, file_name)
    
    columns = hrdata.columns
    for col in columns:
        print(col)
    return 'ok'

def setup_S3_source(workspace, file_name):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3') 
    obj = s3.get_object(Bucket= bucket, Key= file_name)
    return pd.read_csv(obj['Body'])

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')

answer('1')

