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
    
def get_friendly_datatype(datatype, isShortList):
    if (datatype == 'string'):
        return 'List of Text Values' if isShortList else 'Text'
    if ('int' in datatype):
        return 'List of Integer Numbers' if isShortList else 'Integer Number'
    if ('float' in datatype):
        return 'List of Decimal Numbers' if isShortList else 'Decimal Number'
    if (datatype == 'bool'):
        return 'Yes/No'
    if (datatype == 'datetime'):
        return 'List of Date/Times' if isShortList else 'Date/Time'
    
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
    fields = context.dataset.columns
    samples = context.dataset.sample(5)
    length = len(context.dataset)
    fieldRank = 0
    for col in fields:
        columnIndex = fields.get_loc(col)
        values = context.dataset[col].unique()
        datatype = get_datatype(context.dataset,col)
        isShortList = True if (len(values) < context.unique_value_limit) else False
        friendlyDatatype = get_friendly_datatype(datatype, isShortList)
        fieldName = str(col)
        uniqueLength = len(values)
        cardinalityRatio = uniqueLength/length
        fieldID = getFieldID(col,fieldName,context)
        put_field(context, fieldID, fieldName, columnIndex, datatype, friendlyDatatype, uniqueLength, cardinalityRatio, fieldRank, samples)
        if (isShortList):
            valueRank=1
            for value in values:
                valueName = str(value)
                valueID = getValueID(value,valueName,col,fieldName,context)
                put_value(context,valueID,valueName,valueRank,fieldID,fieldName,fieldRank)
                valueRank += 1
        fieldRank += 1
        
        
def put_field(context, fieldID, fieldName, columnIndex, datatype, friendlyDatatype, uniqueLength, cardinalityRatio, fieldRank, samples):
    put = context.table.put_item(
        Item={
            'item_id': fieldID,
            'field_id': fieldID,
            'text': fieldName,
            'storage_source': 'dataset',
            'query_part': 'info-field',
            'data_type': datatype,
            'friendly_data_type': friendlyDatatype,
            'data_set_name': context.file_name,
            'unique_value_count': uniqueLength,
            'cardinality_ratio': str(cardinalityRatio),
            'create_time': str(datetime.datetime.now()),
            'workspace': context.workspace,
            'field_rank': fieldRank,
            'value_rank': 0,
            'sample_1': str(samples.iloc[0,[columnIndex]].values[0]),
            'sample_2': str(samples.iloc[1,[columnIndex]].values[0]),
            'sample_3': str(samples.iloc[2,[columnIndex]].values[0]),
            'sample_4': str(samples.iloc[3,[columnIndex]].values[0]),
            'sample_5': str(samples.iloc[4,[columnIndex]].values[0]),
        }
    )
        
def put_value(context, valueID, valueName, valueRank, fieldID, fieldName, fieldRank):
    put = context.table.put_item(
        Item={
            'item_id': valueID,
            'parent_field_id': fieldID,
            'parent_field_name': fieldName,
            'text': valueName,
            'storage_source': 'dataset',
            'query_part': 'info-value',
            'data_set_name': context.file_name,
            'create_time': str(datetime.datetime.now()),
            'workspace': context.workspace,
            'field_rank': fieldRank,
            'value_rank': valueRank,
        }
    )
    
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

# # Remember to comment out the "delete all workspaces" method before testing, and only put it back in when it's fully successful.  
# # If this re-read fails, data will be deleted and Info IDs will be lost
# re_read_all_datasets()

# # -----ENSURE ALL FUNCTIONS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#
