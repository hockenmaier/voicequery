import json
import boto3
import uuid

def lambda_handler(event, context):
    jsonData = transcribe(event['blob'])
    return jsonData

def transcribe(blob):
    store_blob_s3(blob)
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    return data

def store_blob_s3(blob):
    bucket = "voicequery-transcribe"
    s3 = boto3.client('s3')
    filename = 'temptranscribe_'+ str(uuid.uuid4()) +'.wav'
    print(blob)
    binary_message = blob.encode('utf-8')
    # fileBlob = blob.read()
    s3.put_object(Bucket= bucket, Body= blob, Key= filename)

# # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

# # To use this test, the binary created here must be directly passed as the body to the s3 put command
# binary_data = b'\x00\xFF\x00\xFF'
# transcribe(binary_data)

# # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#