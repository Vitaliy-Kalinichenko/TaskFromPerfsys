import json
import boto3
import os

S3_BUCKET = os.environ['S3_BUCKET']
S3_BUCKET_ARN = os.environ['S3_BUCKET_ARN']
BLOBS_TABLE = os.environ['BLOBS_TABLE']
dynamodb_client = boto3.client("dynamodb")


def labelOnS3Upload(event, context):
    blob_id = event['Records'][0]['s3']['object']['key']

    client = boto3.client("rekognition", region_name=os.environ['REGION'],
                          aws_access_key_id=os.environ['ACCESS_KEY'],
                          aws_secret_access_key=os.environ['SECRET_KEY']
                          )
    response = client.detect_labels(
        Image={
            "S3Object": {
                "Bucket": S3_BUCKET,
                'Name': blob_id
            }
        },
        MaxLabels=100,
        MinConfidence=70
    )

    # Get the labels
    labels = response['Labels']

    # Add to DynamoDB
    add_labels_to_db(labels, blob_id)

    return labels


def add_labels_to_db(labels, blob_id):
    imageLabels = []

    for label in labels:
        parents = []
        for parent in label.get("Parents"):
            parents.append(parent.get("Name"))

        imageLabels.append({
            "label": label.get("Name"),
            "confidence": label.get("Confidence"),
            "parents": parents
        })

    imageLabels_data = json.dumps(imageLabels)

    dynamodb_client.update_item(
        TableName=BLOBS_TABLE,
        Key={
            'blob_id': {"S": blob_id},
        },
        UpdateExpression='SET labels=:value',
        ExpressionAttributeValues={
            ":value": {"S": imageLabels_data}
        }
    )

    return imageLabels_data
