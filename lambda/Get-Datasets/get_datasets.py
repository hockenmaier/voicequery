import json
import boto3
import datetime

def lambda_handler(event, context):
    jsonData = get_datasets(event['userID'])
    return jsonData

def get_datasets(userID):
    bucket = "voicequery-datasets"
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket= bucket, Prefix= userID + '/')
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    data['objects'] = objects
    dataDump = (json.dumps(data, default = date_converter))
    print(dataDump)
    return dataDump
    
def date_converter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    
# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

get_datasets('voicequery-user')

# # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#