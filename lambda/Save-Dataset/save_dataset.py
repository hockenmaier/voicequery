import json
import boto3
from botocore.exceptions import ClientError
import logging


def lambda_handler(event, context):
    jsonData = save_dataset(event['workspace'], event['filename'], event['filetype'])
    return jsonData

def save_dataset(workspace, filename, filetype):
    context = create_context(workspace,filename,filetype)
    url = create_presigned_url(context)
    data = {}
    data['statusCode'] = '200'
    data['version'] = "0.0.1"
    data['presignedurl'] = url
    data['fileName'] = context.userID + '/' + context.filename
    print(data)
    return data
    
class contextObject:
    def __init__(self):
        self.workspace = ''
        self.filename = ''
        self.filetype = ''
        self.bucket = ''
        self.s3 = None
        self.userID = ''

def create_context(workspace,filename,filetype):
    newContext = contextObject()
    newContext.workspace = workspace
    newContext.bucket = "voicequery-datasets"
    newContext.userID = "voicequery-user"
    newContext.filename = filename
    newContext.filetype = filetype
    newContext.s3 = boto3.client('s3')
    return newContext
    
def create_presigned_url(context, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    try:
        response = context.s3.generate_presigned_url('put_object',
            Params={'Bucket': context.bucket,
                    'Key': context.userID + '/' + context.workspace + '/' + context.filename,
                    'ContentType': context.filetype},
            ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response