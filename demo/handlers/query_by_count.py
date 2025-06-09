import json
from aws_helpers import get_dynamodb_table

def lambda_handler(event, context):
    # Parse JSON body to get tag counts
    body = json.loads(event.get('body', '{}'))
    table = get_dynamodb_table()

    # Scan entire table and filter by required tag counts
    response = table.scan()
    matching_urls = []
    for item in response.get('Items', []):
        tags = item.get('tags', {})
        if all(tags.get(tag, 0) >= count for tag, count in body.items()):
            # Return thumbnail URL for images, or original URL for other media
            matching_urls.append(item.get('thumbUrl') or item.get('originalUrl'))

    return {
        'statusCode': 200,
        'body': json.dumps({'links': matching_urls})
    }
