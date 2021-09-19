<!--
title: 'AWS API for recognition of images'
layout: Doc
framework: v2
platform: AWS
language: python
authorLink: 'https://github.com/Vitaliy-Kalinichenko'
authorName: 'Kalinichenko Vitaliy'
-->

# AWS API for recognition of images

This example demonstrates how to setup API for recognition of images
using [Presigned URLs](http://boto3.readthedocs.io/en/latest/guide/s3.html?highlight=presigned#generating-presigned-urls)
to uploads images.

The initial POST creates entry in dynamo and returns a presigned upload URL. This is used to upload the asset without
needing any credentials. After uploading image a s3 event triggers another lambda method for recognition of image. **AWS
Rekognition** is used for detecting labels in image.

This project uses `serverless` framework.

## Deployment

### MacOS/Linux

- Create yourself AWS account using
  the [link](https://portal.aws.amazon.com/billing/signup?redirect_url=https%3A%2F%2Faws.amazon.com%2Fregistration-confirmation&language=ru_ru#/start)
  .
- Use the [tutorial](https://www.serverless.com/framework/docs/providers/aws/guide/credentials/) to create a user.

To install the latest version serverless, run this command in your terminal:

```
curl -o- -L https://slss.io/install | bash
$ serverless login
```

Install the necessary plugins

```
$ sls plugin install -n serverless-python-requirements
$ sls plugin install -n serverless-dotenv-plugin
$ sls plugin install -n serverless-s3-remover
```

In the api_files folder, rename the ```exe.env``` file to ```.env```, after which we fill in the environment variables
necessary for deployment

```
REGION=aws_region
ACCESS_KEY=your_access_key
SECRET_KEY=your_secret_key
USER_ARN=arn_your_user
```

> USER_ARN you can find on the page of the user AWS you created.
>
Launching the deployment api

```
$ sls deploy
```

After running deploy, you should see output similar to:

```bash
Serverless: Packaging service...
Serverless: Excluding development dependencies...
Serverless: Injecting required Python packages to package...
Serverless: Installing dependencies for custom CloudFormation resources...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service testPervsys.zip file to S3 (47.02 MB)...
Serverless: Uploading custom CloudFormation resources...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
............................
Serverless: Stack update finished...
Service Information
service: testPervsys
stage: test
region: eu-central-1
stack: testPervsys-test
resources: 26
api keys:
  None
endpoints:
  GET - https://xxxxxxx.execute-api.eu-central-1.amazonaws.com/test/blobs/{blob_id}
  POST - https://xxxxxxx.execute-api.eu-central-1.amazonaws.com/test/blobs
functions:
  getUser: testPervsys-test-getUser
  createUser: testPervsys-test-createUser
  labelOnS3Upload: testPervsys-test-labelOnS3Upload
layers:
  None
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments,
you might want to configure an authorizer. For details on how to do that, refer
to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

## Description API

This api implements two endpoints

- POST .../blobs
- GET .../blobs/{blob_id}

When use POST endpoint, the request body must contain a callback url where you expect the result of the service.
### Get image pre-signed upload URL

```bash
$ curl -H "Content-Type: application/json" -X -d '{"callback_url": "http://your_callback_url.com"}' 
POST https://xxxxxxx.execute-api.eu-central-1.amazonaws.com/dev/blobs
```

Response API for POST request

```bash
{
    "blob_id": "d224aff1-2d15-47b8-a4c1-c44ea068715b",
    "callback_url": "http://your_callback_url.com",
    "upload_url": "https://blobs-bucket-s3-uploader.s3.amazonaws.com/d224aff1-2d15-47b8-a4c1-c44ea068715b?..."
}
```

> ```"blob_id"```: id records in the DynamoDB database where the result of the work will be recorded images recognition.  
```"callback_url"```: url for callback when the result of image recognition is ready  
```"upload_url"```: the link where the client uploading image for recognition. Put request type. The link is valid for 5 min.
>

### Upload a file to the URL

```bash
$ curl --location --request PUT "<upload_url>" --header 'Content-Type: image/jpeg' --data-binary 'file-path'
```

### Response API for GET requests

```bash
$ curl -H "Content-Type: application/json" -X GET  https://xxxxxxx.exe
cute-api.eu-central-1.amazonaws.com/dev/blobs/d224aff1-2d15-47b8-a4c1-c44ea068715b
{
    "blob_id": "d224aff1-2d15-47b8-a4c1-c44ea068715b",
    "labels": [
        {
            "label": "Scenery",
            "confidence": 99.84720611572266,
            "parents": [
                "Outdoors",
                "Nature"
            ]
        },
        ...
```

> ```"blob_id"```: id of the requested entry in the database  
> ```"labels"```: image recognition results