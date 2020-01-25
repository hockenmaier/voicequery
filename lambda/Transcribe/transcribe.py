import json
import boto3
import uuid
import codecs
import base64
import time
import urllib.request

def lambda_handler(event, context):
    jsonData = transcribe(event['blobdata'], event['workspace'])
    # jsonData = transcribe(event, '1')
    return jsonData

def transcribe(blob, workspace):
    context = create_context(blob, workspace)
    store_blob_s3(context)
    call_transcribe(context)
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    return data
    
class contextObject:
    def __init__(self):
        self.blobdata = None
        self.workspace = ''
        self.filename = ''

def create_context(blob,workspace):
    newContext = contextObject()
    newContext.blobdata = blob
    newContext.workspace = workspace
    return newContext

def store_blob_s3(context):
    print(type(context.blobdata))
    bucket = "voicequery-transcribe"
    s3 = boto3.client('s3')
    context.filename = 'temptranscribe_'+ str(uuid.uuid4()) +'.wav'
    # print('blobdata: ' + str(context.blobdata))
    print('workspace: ' + str(context.workspace))
    # print(context.blobdata[0])
    # binary_data = context.blobdata.encode('utf-8')
    # print(type(binary_data))
    # base64_data = codecs.decode(binary_data, 'base64')
    # print(type(base64_data))
    base64_decoded_data = base64.standard_b64decode(context.blobdata)
    print(type(base64_decoded_data))
    # base64_decoded_data = base64.standard_b64decode(context.blobdata + "===")
    # base64_decoded_data = base64.b64decode(context.blobdata + "===")
    # fileBlob = blob.read()
    s3.put_object(Bucket= bucket, Body= base64_decoded_data, Key= context.filename)
    
def call_transcribe(context):
    transcribe = boto3.client('transcribe')
    job_name = context.filename + '_job'
    job_uri = "https://voicequery-transcribe.s3-us-west-2.amazonaws.com/female_doctorate_test.wav"
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US'
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    print('Status: ')
    print(status)
    print(status['TranscriptionJob']['Transcript'])
    print(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
    byte_contents = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri']).read()
    contents = json.loads(byte_contents.decode('utf-8'))
    print('Contents: ')
    print(contents)
    print(contents['results']['transcripts']['transcript'])

# # # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

# # To use this test, the binary created here must be directly passed as the body to the s3 put command
binary_data = b'\x00\xFF\x00\xFF'
transcribe(binary_data, 'test')

# # # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#