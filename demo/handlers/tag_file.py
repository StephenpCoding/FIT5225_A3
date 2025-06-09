import os
import json
import boto3
from aws_helpers import get_s3_client, get_dynamodb_table, get_bucket_names, invoke_model

def lambda_handler(event, context):
    # Initialize S3 client, DynamoDB table, and bucket names
    s3 = get_s3_client()
    table = get_dynamodb_table()
    raw_bucket, thumb_bucket = get_bucket_names()

    # Triggered for each uploaded file
    for record in event['Records']:
        key = record['s3']['object']['key']
        original_url = f"https://{raw_bucket}.s3.amazonaws.com/{key}"

        # Invoke pretrained model to detect bird species
        tags = invoke_model(raw_bucket, key)

        # Determine thumbnail URL
        thumb_key = key.rsplit('.', 1)[0] + '-thumb.jpg'
        thumb_url = f"https://{thumb_bucket}.s3.amazonaws.com/{thumb_key}"

        # Store metadata and tags in DynamoDB
        item = {
            'fileId': key,
            'originalUrl': original_url,
            'thumbUrl': thumb_url,
            'tags': tags,
            'uploadedAt': int(context.aws_request_id[:8], 16)
        }
        table.put_item(Item=item)

    # 1. Construct the notification message payload
    message = {
        'fileId': key,
        'originalUrl': original_url,
        'tags': tags,
        'uploadedAt': item['uploadedAt']
    }
    # 2. Format each tag as a message attribute for SNS filtering
    msg_attrs = {
        tag: {
            'DataType': 'Number',
            'StringValue': str(count)
        } for tag, count in tags.items()
    }
    # 3. Publish the message to the SNS topic with attributes for filtering
    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(message),
        MessageAttributes=msg_attrs
    )

    return {'statusCode': 200, 'body': json.dumps({'message': 'File tagged and metadata stored'})}