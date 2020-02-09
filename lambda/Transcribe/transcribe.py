import json
import boto3
from botocore.exceptions import ClientError
import uuid
import codecs
import base64
import time
import urllib.request
import logging

def lambda_handler(event, context):
    jsonData = transcribe(event['workspace'], event['option'], event['filename'])
    return jsonData

def transcribe(workspace,option,filename):
    context = create_context(workspace,option,filename)
    # store_blob_s3(context)
    if(option == 'geturl'):
        url = create_presigned_url(context)
        data = {}
        data['statusCode'] = '200'
        data['version'] = "0.0.1"
        data['presignedurl'] = url
        data['fileName'] = context.filename
        print(data)
        return data
    else:
        transcription = call_transcribe(context)
        data = {}
        data['statusCode'] = '200'
        data['version'] = "0.0.1"
        data['transcription'] = transcription
        print(data)
        return data
    
class contextObject:
    def __init__(self):
        # self.blobdata = None
        self.workspace = ''
        self.filename = ''
        self.bucket = ''
        self.s3 = None

def create_context(workspace,option,filename):
    newContext = contextObject()
    # newContext.blobdata = blob
    newContext.workspace = workspace
    newContext.bucket = "voicequery-transcribe"
    if(option == 'geturl'):
        newContext.filename = 'temptranscribe_'+ str(uuid.uuid4()) +'.wav'
        # newContext.filename = 'temptranscribe_test1234.wav'
    else:
        newContext.filename = filename
    newContext.s3 = boto3.client('s3')
    return newContext
    
def create_presigned_url(context, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    # Generate a presigned URL for the S3 object
    try:
        response = context.s3.generate_presigned_url('put_object',
                                                    Params={'Bucket': context.bucket,
                                                            'Key': context.filename,
                                                            # 'Region': 'us-west-2',
                                                            # 'ContentType': 'multipart/form-data'},
                                                            'ContentType': 'audio/wav'},
                                                            # 'ACL': 'public-read',
                                                            # 'ContentMD5': 'false'},
                                                    # HttpMethod='Put',
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def call_transcribe(context):
    transcribe = boto3.client('transcribe')
    job_name = context.filename + '_job'
    # job_uri = "https://voicequery-transcribe.s3-us-west-2.amazonaws.com/female_doctorate_test.wav"
    job_uri = "https://voicequery-transcribe.s3-us-west-2.amazonaws.com/" + context.filename
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
    byte_contents = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri']).read()
    contents = json.loads(byte_contents.decode('utf-8'))
    print('Contents: ')
    print(contents)
    return contents['results']['transcripts'][0]['transcript']
    
def list_to_dict(lst): 
    res_dct = {lst[i]: lst[i+1] for i in range(0, len(lst), 2)} 
    return res_dct 

# # # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#

# # # To use this test, the binary created here must be directly passed as the body to the s3 put command
# binary_data = b'\x00\xFF\x00\xFF'
# transcribe('test','geturl','')

# transcribe('test','gettranscription','female_doctorate_test.wav')

# # # # -----ENSURE ALL TEST RUNS ARE COMMENTED OUT BEFORE DEPLOYING TO LAMBDA------------------#