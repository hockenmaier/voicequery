import json
import boto3
import datetime

def lambda_handler(event, context):
    jsonData = get_datasets(event['workspace'],event['userID'])
    return jsonData

def get_datasets(workspace,userID):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket= bucket, Prefix= userID + '/' + workspace + '/')
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    data['objects'] = objects
    print(json.dumps(data, default = date_converter))
    return data
    
def date_converter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    
# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

get_datasets('Sales Workspace', 'voicequery-user')

# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#