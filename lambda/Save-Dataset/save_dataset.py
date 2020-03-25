import json
import boto3
from botocore.exceptions import ClientError
import logging


def lambda_handler(event, context):
    jsonData = save_dataset(event['workspace'], event['filename'], event['filetype'], event['option'])
    return jsonData

def save_dataset(workspace, filename, filetype, option):
    context = create_context(workspace,filename,filetype)
    if (option == 'geturl'):
        url = create_presigned_url(context)
        data = {}
        data['statusCode'] = '200'
        data['version'] = "0.0.1"
        data['presignedurl'] = url
        data['fileName'] = context.userID + '/' + context.filename
        data['note'] = "presigned url successfully generated"
        print(data)
    elif (option == 'delete'):
        delete_file(context)
        # TO DO:  Delete all associated data to workspace in DynamoDB
        data = {}
        data['statusCode'] = '200'
        data['version'] = "0.0.1"
        data['note'] = "file successfully deleted"
        print(data)
    else:
        data = {}
        data['statusCode'] = '400'
        data['version'] = "0.0.1"
        data['note'] = "invalid option"
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
    
def copy_file_to_archive(context):
    try:
        response = client.copy_object(
            Bucket=context.bucket,
            Key='archive' + '/' + context.userID + '/' + context.workspace + '/' + context.filename,
            CopySource={'Bucket':context.bucket, 'Key':context.userID + '/' + context.workspace + '/' + context.filename},
    except ClientError as e:
        logging.error(e)
        return None
    return response
    
def delete_file(context):
    try:
        response = context.s3.delete_object(
            Bucket= context.bucket,
            Key= context.userID + '/' + context.workspace + '/' + context.filename)
    except ClientError as e:
        logging.error(e)
        return None
    return response