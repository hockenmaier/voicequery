import numpy
import pandas as pd
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime

def lambda_handler(event, context):
    jsonData = read_dataset(event['workspace'])
    return jsonData
    
def read_dataset(workspace):
    table = setup_dynamo()
    file_name = "sample-data/HRData_QuickSightSample.csv"
    unique_value_limit = 15
    dataset = setup_S3_source(workspace, file_name)
    jsonData = package_JSON(dataset, unique_value_limit)
    deleteOldFields(table, workspace,file_name)
    storeFields(jsonData, table, workspace, file_name, unique_value_limit)
    print(jsonData)
    return jsonData

def setup_S3_source(workspace, file_name):
    bucket = "voicequery-datasets"
    # file_name = "sample-data/RevenueData_QuickSightSample.csv"
    # file_name = "sample-data/index_2013.csv"
    
    s3 = boto3.client('s3') 
    # 's3' is a key word. create connection to S3 using default config and all buckets within S3
    
    obj = s3.get_object(Bucket= bucket, Key= file_name) 
    # get object and file (key) from bucket
    
    return pd.read_csv(obj['Body'])

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')

def package_JSON(dataset, unique_value_limit):
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    bubbles = []
    columns = dataset.columns
    
    for col in columns:
        # print('column: ' + col)
        bubble = {}
        bubble['internalID'] = ""
        bubble['name'] = str(col)
        bubble['type'] = 'info-field'
        bubble['dataType'] = map_numpy_datatypes(dataset[col].dtype)
        bubble['bubbles'] = []
        unique = dataset[col].unique()
        bubble['unique_value_count'] = len(unique)
        if (len(unique) < unique_value_limit):
            for value in unique:
                # print('unique value: ' + value)
                subBubble = {}
                subBubble['internalID'] = ""
                subBubble['name'] = str(value)
                subBubble['type'] = 'info-value'
                subBubble['bubbles'] = []
                bubble['bubbles'].append(subBubble)
        bubbles.append(bubble)
    data['bubbles'] = bubbles
    #print(data)
    return data
    
def map_numpy_datatypes(dtype):
    stringedType = str(dtype)
    if (stringedType == 'object'):
        return 'string'
    else:
        return stringedType

def storeFields(jsonData, table, workspace, file_name, unique_value_limit):
    for col in jsonData['bubbles']:
        fieldID = str(uuid.uuid4())
        put = table.put_item(
            Item={
                'item_id': fieldID,
                'field_id': fieldID,
                'text': col['name'],
                'storage_source': 'dataset',
                'query_part': 'info-field',
                'data_type': col['dataType'],
                'data_set_name': file_name,
                'unique_value_count': col['unique_value_count'],
                'create_time': str(datetime.datetime.now()),
                'workspace': workspace,
                # 'unique_values': col['bubbles'] #if col['bubbles'] else 'More than ' + str(unique_value_limit) + ' unique values',
            }
        )
        for value in col['bubbles']:
            valueID = str(uuid.uuid4())
            put = table.put_item(
                Item={
                    'item_id': valueID,
                    'field_id': fieldID,
                    'text': value['name'],
                    'storage_source': 'dataset',
                    'query_part': 'info-value',
                    'data_set_name': file_name,
                    'create_time': str(datetime.datetime.now()),
                    'workspace': workspace,
                }
        )

def deleteOldFields(table,workspace,file_name):
    foundItems = table.scan(
                FilterExpression=Key('workspace').eq(workspace) & Key('data_set_name').eq(file_name)
            )
    if(foundItems['Items']):
        for item in foundItems['Items']:
            table.delete_item(
                Key={
                    'item_id': item['item_id'],
                    'text': item['text'],
                }
            )

read_dataset('1')

