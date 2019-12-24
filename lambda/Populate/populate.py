import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    jsonData = populate(event['workspace'],event['getItems'])
    return jsonData
    
def populate(workspace,getItems):
    table = setup_dynamo()
    workspaceItems = get_workspace_data(table, workspace, getItems)
    jsonData = package_JSON(workspaceItems)
    return jsonData

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')

def get_workspace_data(table, workspace, getItems):
    if (getItems == 'lexicon'):
        chosenExpression=Key('workspace').eq(workspace) & (Key('query_part').eq('subject') | Key('query_part').eq('condition'))
    elif (getItems == 'concepts'):
        chosenExpression=Key('workspace').eq(workspace) & Key('query_part').eq('concept')
    foundItems = table.scan(
        FilterExpression = chosenExpression
    )
    return foundItems['Items']
    
def package_JSON(workspaceItems):
        data = {}
        data['statusCode'] = '200'
        data['version'] = "0.0.1"
        bubbles = []
        for item in workspaceItems:
            bubble = {}
            bubble['internalID'] = item['item_id']
            bubble['name'] = item['text']
            bubble['type'] = item['query_part']
            bubble['closestMatchId'] = item['closest_match_id'] if ('closest_match_id' in item) else ''
            bubble['closestMatchText'] = item['closest_match_text'] if ('closest_match_text' in item) else '' 
            bubble['bubbles'] = [] if ('bubbles' in item) else '' 
            bubble['concept_items'] = item['concept_items'] if ('concept_items' in item) else ''
            bubbles.append(bubble)
        data['bubbles'] = bubbles
        return data   #.replace('\/', r'/')