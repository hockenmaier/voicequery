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
    
    hrdata = pd.read_csv(obj['Body']) # 'Body' is a key word
    
    print('Analysis of file: ' + bucket + '/' + file_name)
    
    print(hrdata[0:5])
    for i in range(3):
        print('.')
    print(hrdata[len(hrdata)-5:len(hrdata)])
    print('')
    print('Columns:')
    columns = hrdata.columns
    #TODO: create bubble objects out of column names
    #print(hrdata['Tenure'].unique())
    
    for col in columns:
        print(col)
        print('Unique Values: ')
        unique = hrdata[col].unique()
        if (len(unique) < 50):
            print(unique)
        else:
            print('More that 50 distinct values')
        print('')
    
    
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
        bubble['type'] = 'info-field'  #TODO check name
        bubble['bubbles'] = []
        bubbles.append(bubble)
        unique = hrdata[col].unique()
        if (len(unique) < 15):
            #TODO Create Sub-Bubbles
            print(unique)
        else:
            print('More that 50 distinct values')
        print('')
    data['bubbles'] = bubbles
    return data
    
read_dataset()