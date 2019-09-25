import numpy
import pandas as pd
import json
import boto3
# from csv import DictReader

def lambda_handler(event, context):
    jsonData = read_dataset()
    return jsonData
    
def read_dataset():
    bucket = "voicequery-datasets"
    # file_name = "sample-data/HRData_QuickSightSample.csv"
    # file_name = "sample-data/RevenueData_QuickSightSample.csv"
    file_name = "sample-data/index_2013.csv"
    
    s3 = boto3.client('s3') 
    # 's3' is a key word. create connection to S3 using default config and all buckets within S3
    
    obj = s3.get_object(Bucket= bucket, Key= file_name) 
    # get object and file (key) from bucket
    
    hrdata = pd.read_csv(obj['Body'])
    jsonData = package_JSON(hrdata)
    return jsonData
    
def package_JSON(hrdata):
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    bubbles = []
    columns = hrdata.columns
    
    for col in columns:
        bubble = {}
        bubble['internalID'] = ""
        bubble['name'] = col
        bubble['type'] = 'info-field'
        bubble['bubbles'] = []
        
        unique = hrdata[col].unique()
        if (len(unique) < 15):
            for value in unique:
                subBubble = {}
                subBubble['internalID'] = ""
                subBubble['name'] = value
                subBubble['type'] = 'info-value'
                bubble['bubbles'] = []
                bubble['bubbles'].append(subBubble)
        bubbles.append(bubble)
    data['bubbles'] = bubbles
    print(data)
    return data
    
# read_dataset()