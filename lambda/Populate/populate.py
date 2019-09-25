import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    jsonData = populate(event['workspace'])
    return jsonData
    
def populate(workspace):
    table = setup_dynamo()
    workspaceItems = get_workspace_data(table, workspace)
    jsonData = package_JSON(workspaceItems)
    return jsonData

def setup_dynamo():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('lexicon')

def get_workspace_data(table, workspace):
    foundItems = table.scan(
        FilterExpression=Key('workspace').eq(workspace) & (Key('query_part').eq('subject') | Key('query_part').eq('condition'))
    )
    return foundItems['Items']
    
def package_JSON(workspaceItems):
        data = {}
        data['statusCode'] = '200'
        data['version'] = "0.0.1"
        bubbles = []
        for item in workspaceItems:
            bubble = {}
            bubble['internalID'] = ""
            bubble['name'] = item['text']
            bubble['type'] = item['query_part']
            bubble['bubbles'] = []
            bubbles.append(bubble)
        data['bubbles'] = bubbles
        return data   #.replace('\/', r'/')