import numpy
import pandas as pd
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import datetime
# from decimal import Decimal

def lambda_handler(event, context):
    jsonData = read_dataset(event['workspace'])
    return jsonData
    
def read_dataset(workspace):
    context = create_context(workspace)
    context.file_name = workspace
    # context.file_name = "sample-data/HRData_QuickSightSample.csv"
    # context.file_name = "sample-data/index_2013.csv"
    # context.file_name = "sample-data/SalesPipeline_QuickSightSample.csv"
    context.unique_value_limit = 15
    
    context.dataset = setup_S3_source(context)
    context.table = setup_dynamo()
    context.available_data = get_workspace_data(context)
    
    delete_workspace_data(context)
    calculate_and_store(context)
    
    context.jsonData = package_JSON(context)
    print(context.jsonData)
    return context.jsonData

class contextObject:
    def __init__(self):
        self.workspace = ''
        self.file_name = ''
        self.unique_value_limit = 0
        self.dataset = None
        self.table = None
        self.jsonData = {}
        self.available_data = {}

def create_context(workspace):
    newContext = contextObject()
    newContext.workspace = workspace
    return newContext

def setup_S3_source(context):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket= bucket, Key= context.file_name)
    return readAnyType(obj['ContentType'],obj['Body'])
    
def readAnyType(contentType, body):
    if (contentType == 'text/csv'):
        return pd.read_csv(body)
    elif (contentType == 'application/vnd.ms-excel') | (contentType == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        return pd.read_excel(body)
    elif (contentType =='application/json')|(contentType == 'application/ld+json'):
        return pd.read_json(body)
    elif (contentType == 'text/html'):
        return pd.read_html(body)
    elif (contentType == 'text/plain'):
        return pd.read_fwf(body)
    else:
        return None
    

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')

def get_datatype(df,col):
    dataType = map_numpy_datatypes(df[col].dtype)
    if dataType == 'string':
        try:
            df[col] = pd.to_datetime(df[col])
            dataType = 'datetime'
        except ValueError:
            pass
    return dataType
    
def map_numpy_datatypes(dtype):
    stringedType = str(dtype)
    if (stringedType == 'object'):
        return 'string'
    else:
        return stringedType
        
def get_workspace_data(context):
    foundItems = context.table.scan(
        FilterExpression=Key('workspace').eq(context.workspace) & Key('storage_source').eq('dataset')
    )
    return foundItems['Items']

def delete_workspace_data(context):
    foundItems = context.table.scan(
                FilterExpression=Key('workspace').eq(context.workspace) & Key('data_set_name').eq(context.file_name)
            )
    if(foundItems['Items']):
        for item in foundItems['Items']:
            context.table.delete_item(
                Key={
                    'item_id': item['item_id'],
                    'text': item['text'],
                }
            )

def getFieldID(col, columnName, context):
    existingFieldRecord = searchFields(columnName,context.available_data)
    if existingFieldRecord:
        return existingFieldRecord[0]['item_id']
    else:
        return str(uuid.uuid4())

def searchFields(columnName,data):
    return [element for element in data if (element['query_part'] == 'info-field') & (element['text'] == columnName)]
    
def getValueID(value, valueName, col, columnName, context):
    existingValueRecord = findFirstMatchingValue(valueName,columnName,context.available_data)
    if existingValueRecord:
        return existingValueRecord['item_id']
    else:
        return str(uuid.uuid4())

def findFirstMatchingValue(valueName,columnName,data):
    for element in data:
        if (element['query_part'] == 'info-value'):
            if (element['parent_field_name'] == columnName) & (element['text'] == valueName):
                return element
                

def package_JSON(context):
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    data['note'] = 'successfully read'
    #print(data)
    return data
    
def calculate_and_store(context):
    fields = []
    columns = context.dataset.columns
    samples = context.dataset.sample(5)
    # print('samples:')
    # print(samples)
    length = len(context.dataset)
    fieldRank = 0
    for col in columns:
        columnIndex = columns.get_loc(col)
        # print('col: ' + str(col))
        # print('sample 1: ' + str(samples.iloc[0,[columnIndex]].values[0]))
        # print('sample 5: ' + str(samples.iloc[4,[columnIndex]].values[0]))
        datatype = get_datatype(context.dataset,col)
        columnName = str(col)
        unique = context.dataset[col].unique()
        uniqueLength = len(unique)
        cardinalityRatio = uniqueLength/length
        fieldID = getFieldID(col,columnName,context)
        put = context.table.put_item(
            Item={
                'item_id': fieldID,
                'field_id': fieldID,
                'text': columnName,
                'storage_source': 'dataset',
                'query_part': 'info-field',
                'data_type': datatype,
                'data_set_name': context.file_name,
                'unique_value_count': uniqueLength,
                'cardinality_ratio': str(cardinalityRatio),
                'create_time': str(datetime.datetime.now()),
                'workspace': context.workspace,
                'field_rank': fieldRank,
                'valueRank': 0,
                'sample_1': str(samples.iloc[0,[columnIndex]].values[0]),
                'sample_2': str(samples.iloc[1,[columnIndex]].values[0]),
                'sample_3': str(samples.iloc[2,[columnIndex]].values[0]),
                'sample_4': str(samples.iloc[3,[columnIndex]].values[0]),
                'sample_5': str(samples.iloc[4,[columnIndex]].values[0]),
            }
        )
        fieldRank += 1
        if (len(unique) < context.unique_value_limit):
            valueRank=1
            for value in unique:
                valueName = str(value)
                valueID = getValueID(value,valueName,col,columnName,context)
                put = context.table.put_item(
                    Item={
                        'item_id': valueID,
                        'parent_field_id': fieldID,
                        'parent_field_name': columnName,
                        'text': valueName,
                        'storage_source': 'dataset',
                        'query_part': 'info-value',
                        'data_set_name': context.file_name,
                        'create_time': str(datetime.datetime.now()),
                        'workspace': context.workspace,
                        'field_rank': fieldRank,
                        'valueRank': valueRank,
                    }
                )
                valueRank += 1
    
def re_read_all_datasets():
    print('Retrieving list of datasets')
    datasets = get_datasets()
    for dataset in datasets['Contents']:
        print('Reading Dataset ' + str(dataset))
        try:
            read_dataset(dataset['Key'])
            print('success')
        except:
            print('failed to read dataset')

def get_datasets():
    userID = "voicequery-user"
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket= bucket, Prefix= userID + '/')
    print(objects)
    return objects


# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

# read_dataset('voicequery-user/HR Activity Sample/HRData_QuickSightSample.csv')

# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#



# # -----ENSURE ALL FUNCTIONS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

# re_read_all_datasets()

# # -----ENSURE ALL FUNCTIONS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#
