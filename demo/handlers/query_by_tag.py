import json
from aws_helpers import get_dynamodb_table
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    # Get 'tag' query parameter
    tag = event['queryStringParameters'].get('tag')
    table = get_dynamodb_table()

    # Scan with filter expression to find items containing the tag
    response = table.scan(
        FilterExpression=Attr('tags').contains(tag)
    )

    urls = [item.get('thumbUrl') or item.get('originalUrl') for item in response.get('Items', [])]

    return {
        'statusCode': 200,
        'body': json.dumps({'links': urls})
    }