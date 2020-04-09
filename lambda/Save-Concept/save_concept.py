import sys
import os
sys.path.append(os.path.abspath("../Layers/custom_NLTK/python"))
import nltk
from nltk_vq_utils import setup_nltk_data, get_common_concept_name
from nltk.corpus import wordnet
from nltk.corpus import wordnet_ic
import json
import uuid
import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    json = save_concept(event)
    return json
    
def save_concept(event):
    table = setup_dynamo()
    responseText = ''
    conceptID = ''
    conceptName = event['text']
    if(event['internal_ID'] == '.'): 
        setup_nltk_data()
        return {
        'statusCode': 200,
        'body': 'save-concept booted successfully',
        'conceptID': '',
        'conceptName': ''
        }
    
    if(event['internal_ID'] == ''): 
    # - CREATE ---- A blank ID denotes a brand new concept
        setup_nltk_data()
        conceptName = get_common_concept_name(event['concept_item_detail'][0]['text'],event['concept_item_detail'][1]['text'])
        if conceptName == '':
            conceptName = 'concept'
        conceptID = str(uuid.uuid4())
        put = table.put_item(
            Item=convert_empty_values({
                'item_id': conceptID,
                # 'text': event['text'],
                'text': conceptName,
                'storage_source': 'save_concept',
                'query_part': 'concept',
                'create_time': str(datetime.datetime.now()),
                'workspace': event['workspace'],
                'concept_items': event['concept_items'],
                'concept_item_detail': event['concept_item_detail']
            })
        )
        responseText = 'Concept created successfully'
    elif (event['concept_items']): 
    # - UPDATE ---- A populated ID and populated concept_items field means we need to update an existing concept
        conceptID = event['internal_ID']
        oldText = event['text'] #TODO remove sort key or get the old value from frontend explicitely
        response = table.update_item(
            Key={
                'item_id': conceptID,
                'text': oldText
            },
            # UpdateExpression="set update_time = :u, #text=:t, concept_items = :c",
            UpdateExpression="set update_time = :u, concept_items = :c, concept_item_detail = :d",
            
            ExpressionAttributeValues=convert_empty_values({
                ':u': str(datetime.datetime.now()),
                # ':t': event['text'],
                ':c': event['concept_items'],
                ':d': event['concept_item_detail']
            }),
            # ExpressionAttributeNames={
            #     "#text": "text"
            # },
            ReturnValues="UPDATED_NEW"
        )
        responseText = 'Concept updated successfully'
    else:
    # - DELETE ---- A populated internal ID and blank concept items denotes we need to delete the concept
        conceptID = event['internal_ID']
        oldText = event['text'] #TODO remove sort key or get the old value from frontend explicitely
        response = table.delete_item(
            Key={
                'item_id': conceptID,
                'text': oldText
            },
            ReturnValues="ALL_OLD"
        )
        responseText = 'Concept deleted successfully' 
    return {
        'statusCode': 200,
        'body': json.dumps(responseText),
        'conceptID': conceptID,
        'conceptName': conceptName
    }

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')
    
def convert_empty_values(dictOrList):  #Use this function wrapped around a dyanmo create/update dict in order to make sure there are no empty strings
    if isinstance(dictOrList, dict):
        for key, value in dictOrList.items():
            if isinstance(value, dict) | isinstance(value, list):
                convert_empty_values(value)
            elif value == "":
                dictOrList[key] = None
    elif isinstance(dictOrList, list):
        for value in dictOrList:
            if isinstance(value, dict) | isinstance(value, list):
                convert_empty_values(value)
            elif value == "":
                dictOrList.remove(value)
                dictOrList.append(None)
    return dictOrList
    

# # #-----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#
# with open('test_payloads/test1.json') as f:
#     data = json.load(f)
#     save_concept(data)
# # #-----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

