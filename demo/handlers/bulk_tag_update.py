import json
from aws_helpers import get_dynamodb_table

def lambda_handler(event, context):
    # Parse JSON body for URLs, operation type, and tags
    body = json.loads(event.get('body', '{}'))
    urls = body.get('url', [])
    operation = body.get('operation')  # 1 for add, 0 for remove
    tag_entries = [entry.split(',') for entry in body.get('tags', [])]

    table = get_dynamodb_table()

    # Process each URL to update tags
    for url in urls:
        file_key = url.split('/')[-1]
        response = table.get_item(Key={'fileId': file_key})
        item = response.get('Item', {})
        current_tags = item.get('tags', {})

        for tag, count_str in tag_entries:
            count = int(count_str)
            if operation == 1:
                current_tags[tag] = current_tags.get(tag, 0) + count
            else:
                # Remove or decrement tag count
                current_count = current_tags.get(tag, 0) - count
                if current_count > 0:
                    current_tags[tag] = current_count
                else:
                    current_tags.pop(tag, None)

        # Update DynamoDB item with new tags
        table.update_item(
            Key={'fileId': file_key},
            UpdateExpression='SET tags = :t',
            ExpressionAttributeValues={':t': current_tags}
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Bulk tag update completed'})
    }
