import numpy
import pandas as pd
import json
import boto3
import uuid
import datetime

def lambda_handler(event, context):
    jsonData = read_dataset(event['workspace'])
    return jsonData
    
def read_dataset(workspace):
    table = setup_dynamo()
    file_name = "sample-data/HRData_QuickSightSample.csv"
    hrdata = setup_S3_source(workspace, file_name)
    jsonData = package_JSON(hrdata)
    storeFields(jsonData, table, workspace, file_name)
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
    
def storeFields(jsonData, table, workspace, file_name):
    for col in jsonData['bubbles']:
        fieldID = str(uuid.uuid4())
        put = table.put_item(
            Item={
                'item_id': fieldID,
                'text': col['name'],
                'data_type': col['dataType'],
                'data_set': file_name,
                'create_time': str(datetime.datetime.now()),
                'workspace': workspace,
                'unique_values': col['bubbles']
            }
        )

def package_JSON(hrdata):
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    bubbles = []
    columns = hrdata.columns
    
    for col in columns:
        # print('column: ' + col)
        bubble = {}
        bubble['internalID'] = ""
        bubble['name'] = str(col)
        bubble['type'] = 'info-field'
        bubble['dataType'] = map_numpy_datatypes(hrdata[col].dtype)
        bubble['bubbles'] = []
        
        unique = hrdata[col].unique()
        if (len(unique) < 15):
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
    print(data)
    return data
    
def map_numpy_datatypes(dtype):
    stringedType = str(dtype)
    if (stringedType == 'object'):
        return 'string'
    else:
        return stringedType
    
read_dataset('1')

