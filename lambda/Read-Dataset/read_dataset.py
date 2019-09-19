import json
import boto3
from csv import DictReader

def lambda_handler(event, context):
    jsonData = read_dataset()
    return jsonData
    
def read_dataset():
    s3 = boto3.resource(u's3')
    bucket = s3.Bucket(u'voicequery-datasets')
    obj = bucket.Object(key=u'sample-data/HRData_QuickSightSample.csv')
    response = obj.get()
    
    lines = response[u'Body'].read().split()
    for row in DictReader(lines):
        print(row)
    
    jsonData = package_JSON()
    return jsonData
    
def package_JSON():
    data = {}
    return data
    
read_dataset()