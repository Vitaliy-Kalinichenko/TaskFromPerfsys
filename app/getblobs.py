import boto3
import os
import json


dynamodb_client = boto3.client("dynamodb")

BLOBS_TABLE = os.environ['BLOBS_TABLE']


def get_blob(event, context):
    blob_id = event["pathParameters"]["blob_id"]
    result = dynamodb_client.get_item(
        TableName=BLOBS_TABLE,
        Key={"blob_id": {"S": blob_id}}
    )

    item = result.get('Item')
    if not item:
        body = {"error": "Blob not found"}
        return {"statusCode": 404, "body": json.dumps(body)}

    body = {
        "blob_id": item.get("blob_id").get("S"),
        "labels": json.loads(item.get("labels", {"S": "[]"}).get("S"))
    }
    return {"statusCode": 200, "body": json.dumps(body)}
