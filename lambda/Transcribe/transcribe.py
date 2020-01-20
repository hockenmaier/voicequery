import json
import boto3

def lambda_handler(event, context):
    jsonData = transcribe(event)
    return jsonData

def transcribe(event):
    store_blob_s3(event['blob'])
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    return data

def store_blob_s3(blob):
    bucket = "voicequery-transcribe"
    s3 = boto3.client('s3')
    file = open('temptranscribe.wav', 'wb')
    fileBlob = blob.read()
    file.write(fileBlob)
    file.close()
    s3.put_object(Bucket= bucket, Body= file)
    # obj = s3.get_object(Bucket= bucket, Key= context.file_name)