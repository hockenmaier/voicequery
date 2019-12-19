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
    if(event['internal_ID'] == ''): #This denotes a brand new concept
        conceptID = str(uuid.uuid4())
        put = table.put_item(
            Item=convert_empty_values({
                'item_id': conceptID,
                'text': event['text'],
                'storage_source': 'save_concept',
                'query_part': 'concept',
                'create_time': str(datetime.datetime.now()),
                'workspace': event['workspace'],
                'concept_items': event['concept_items']
            })
        )
        responseText = 'Concept created successfully'
    else: #This denotes we need to update an existing concept
        conceptID = event['internalID']
        
        #TODO: update logic
        response = table.update_item( #-----------------SAMPLE from AWS
            Key={
                'item_id': conceptID
            },
            UpdateExpression="set update_time = :update_time, 'text'=:'text', 'concept_items' = :'concept_items'",
            ExpressionAttributeValues={
                'update_time': str(datetime.datetime.now()),
                'text': event['text'],
                'concept_items': event['concept_items']
            },
            ReturnValues="UPDATED_NEW"
        )
        responseText = 'Concept updated successfully'
    return {
        'statusCode': 200,
        'body': json.dumps(responseText),
        'conceptID': conceptID
    }

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')
    
def convert_empty_values(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            convert_empty_values(value)
        elif isinstance(value, list):
            for item in value:
                convert_empty_values(item)
        elif value == "":
            dictionary[key] = None
    return dictionary