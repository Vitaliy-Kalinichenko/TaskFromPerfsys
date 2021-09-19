import os
import uuid
import json

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

BLOBS_TABLE = os.environ['BLOBS_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']
dynamodb_client = boto3.client("dynamodb")


def create_blob(event, context):
    event_body = event.get("body")
    response_body = {"statusCode": 400, "body": json.dumps({"error": "Invalid callback url supplied"})}
    if not event_body:
        return response_body

    request_body = json.loads(event_body)

    callback_url = request_body.get("callback_url")
    if not callback_url:
        return response_body
    
    blob_id = str(uuid.uuid4())

    dynamodb_client.put_item(
        TableName=BLOBS_TABLE,
        Item={
            'blob_id': {'S': blob_id},
            'callback_url': {'S': callback_url},
        }
    )
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'),
                      region_name=os.environ['REGION'],
                      aws_access_key_id=os.environ['ACCESS_KEY'],
                      aws_secret_access_key=os.environ['SECRET_KEY'])
    try:
        upload_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': S3_BUCKET, 'Key': blob_id},
            ExpiresIn=300)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'blob_id': blob_id,
                'callback_url': callback_url,
                'upload_url': upload_url,
            })
        }

    except ClientError as e:
        return e
