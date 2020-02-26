import json
import boto3
from botocore.exceptions import ClientError
import logging
# import magic


def lambda_handler(event, context):
    jsonData = save_dataset(event['workspace'],event['filename'],event['filetype'])
    return jsonData

def save_dataset(workspace,filename, filetype):
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
        # self.blobdata = None
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
    newContext.userID = "test-userid-1988"
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
    # Generate a presigned URL for the S3 object
    # mime = magic.Magic(mime=True)
    try:
        response = context.s3.generate_presigned_url('put_object',
            Params={'Bucket': context.bucket,
                    # 'Key': context.filename},
                    'Key': context.userID + '/' + context.filename,
                    # 'Key': 'testfolder/drop.jpg'},
                    # 'Workspace': context.workspace},
                    'ContentType': context.filetype},
                    # 'ContentType': mime.from_file(context.filename)},
                    # 'ACL': 'public-read',
                    # 'ContentMD5': 'false'},
            # HttpMethod='Put',
            ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response