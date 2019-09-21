import numpy
import pandas as pd
import json
import boto3
# from csv import DictReader

def lambda_handler(event, context):
    jsonData = read_dataset()
    return jsonData
    
def read_dataset():
    # s3 = boto3.resource(u's3')
    # bucket = s3.Bucket(u'voicequery-datasets')
    # obj = bucket.Object(key=u'sample-data/HRData_QuickSightSample.csv')
    # response = obj.get()
    
    # lines = response[u'Body'].read().split()
    # print(response['Body'].
    
    # reader = DictReader(response[u'Body'].read())
    # print(dir(reader))
    # print(reader.fieldnames)
    
    # with open(response[u'Body'].read()) as csvfile:
    #     reader = DictReader(csvfile)
        # print(reader.line_num)
        # for row in reader:
        #     print(row)
    
    # reader = DictReader(file)
    # print(reader.fieldnames)
    
    bucket = "voicequery-datasets"
    file_name = "sample-data/HRData_QuickSightSample.csv"
    
    s3 = boto3.client('s3') 
    # 's3' is a key word. create connection to S3 using default config and all buckets within S3
    
    obj = s3.get_object(Bucket= bucket, Key= file_name) 
    # get object and file (key) from bucket
    
    initial_df = pd.read_csv(obj['Body']) # 'Body' is a key word
    
    print(initial_df)
    
    jsonData = package_JSON()
    return jsonData
    
def package_JSON():
    data = {}
    return data
    
read_dataset()