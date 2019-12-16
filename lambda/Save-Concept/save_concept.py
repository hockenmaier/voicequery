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
    if(event['internalID'] == ''): #This denotes a brand new concept
        conceptID = str(uuid.uuid4())
        put = table.put_item(
            Item={
                'item_id': conceptID,
                'text': event['text'],
                'storage_source': 'save_concept',
                'query_part': 'concept',
                'create_time': str(datetime.datetime.now()),
                'workspace': event['workspace'],
            }
        )
    else: #This denotes we need to update an existing concept
        conceptID = event['internalID']
        
        #TODO: update logic
        # response = table.update_item( #-----------------SAMPLE from AWS
        #     Key={
        #         'year': year,
        #         'title': title
        #     },
        #     UpdateExpression="set info.rating = :r, info.plot=:p, info.actors=:a",
        #     ExpressionAttributeValues={
        #         ':r': decimal.Decimal(5.5),
        #         ':p': "Everything happens all at once.",
        #         ':a': ["Larry", "Moe", "Curly"]
        #     },
        #     ReturnValues="UPDATED_NEW"
        # )
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')