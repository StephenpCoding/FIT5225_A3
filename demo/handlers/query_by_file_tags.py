import json
from aws_helpers import get_dynamodb_table, invoke_model_file

def lambda_handler(event, context):
    # Assume request body contains base64-encoded file content
    file_content = event['body']

    # Invoke model to detect tags from the uploaded file
    tags = invoke_model_file(file_content)
    table = get_dynamodb_table()

    # Scan table and filter by detected tag counts
    response = table.scan()
    matching_urls = []
    for item in response.get('Items', []):
        existing_tags = item.get('tags', {})
        if all(existing_tags.get(tag, 0) >= count for tag, count in tags.items()):
            matching_urls.append(item.get('thumbUrl') or item.get('originalUrl'))

    return {
        'statusCode': 200,
        'body': json.dumps({'links': matching_urls})
    }
