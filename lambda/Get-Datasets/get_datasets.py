import json
import boto3

def lambda_handler(event, context):
    jsonData = get_datasets(event['workspace'],event['userID'])
    return jsonData

def get_datasets(workspace,userID):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3')
    objects = s3.list_objects(Bucket= bucket)
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    data['objects'] = objects
    print(data)
    return data
    
# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

get_datasets('1', 'test-userid-1988')

# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#