import json
from aws_helpers import get_s3_client, get_dynamodb_table, get_bucket_names

def lambda_handler(event, context):
    # Parse JSON body for URLs to delete
    body = json.loads(event.get('body', '{}'))
    urls = body.get('url', [])

    s3 = get_s3_client()
    table = get_dynamodb_table()
    raw_bucket, thumb_bucket = get_bucket_names()

    for url in urls:
        file_key = url.split('/')[-1]
        # Delete original file and thumbnail from S3
        s3.delete_object(Bucket=raw_bucket, Key=file_key)
        thumb_key = file_key.rsplit('.', 1)[0] + '-thumb.jpg'
        s3.delete_object(Bucket=thumb_bucket, Key=thumb_key)

        # Delete record from DynamoDB
        table.delete_item(Key={'fileId': file_key})

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Files and records deleted'})
    }