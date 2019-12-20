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
        conceptID = event['internal_ID']
        oldText = event['text'] #TODO remove sort key or get the old value from frontend explicitely
        response = table.update_item( #-----------------SAMPLE from AWS
            Key={
                'item_id': conceptID,
                'text': oldText
            },
            # UpdateExpression="set update_time = :u, #text=:t, concept_items = :c",
            UpdateExpression="set update_time = :u, concept_items = :c",
            
            ExpressionAttributeValues={
                ':u': str(datetime.datetime.now()),
                # ':t': event['text'],
                ':c': event['concept_items']
            },
            # ExpressionAttributeNames={
            #     "#text": "text"
            # },
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

# # #-----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#
# with open('test_payloads/test1.json') as f:
#     data = json.load(f)
#     save_concept(data)
# # #-----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

