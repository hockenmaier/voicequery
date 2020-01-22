import json
import boto3
import uuid
import codecs

def lambda_handler(event, context):
    jsonData = transcribe(event['blobdata'], event['workspace'])
    return jsonData

def transcribe(blob, workspace):
    context = create_context(blob, workspace)
    store_blob_s3(context)
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    return data
    
class contextObject:
    def __init__(self):
        self.blobdata = None
        self.workspace = ''

def create_context(blob,workspace):
    newContext = contextObject()
    newContext.blobdata = blob
    newContext.workspace = workspace
    return newContext

def store_blob_s3(context):
    bucket = "voicequery-transcribe"
    s3 = boto3.client('s3')
    filename = 'temptranscribe_'+ str(uuid.uuid4()) +'.wav'
    # print('blobdata: ' + str(context.blobdata))
    print('workspace: ' + str(context.workspace))
    # print(context.blobdata[0])
    binary_data = context.blobdata.encode('utf-8')
    base64_data = codecs.encode(binary_data, 'base64')
    # fileBlob = blob.read()
    s3.put_object(Bucket= bucket, Body= binary_data, Key= filename)

# # # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

# # To use this test, the binary created here must be directly passed as the body to the s3 put command
# binary_data = b'\x00\xFF\x00\xFF'
# transcribe(binary_data, 'test')

# # # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#