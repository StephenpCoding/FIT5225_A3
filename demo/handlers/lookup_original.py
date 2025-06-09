import json
from aws_helpers import get_dynamodb_table
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Get 'thumbUrl' query parameter
    thumb_url = event['queryStringParameters'].get('thumbUrl')
    table = get_dynamodb_table()

    # Query DynamoDB using a secondary index on thumbUrl
    response = table.query(
        IndexName='thumbUrl-index',
        KeyConditionExpression=Key('thumbUrl').eq(thumb_url)
    )

    items = response.get('Items', [])
    original_url = items[0].get('originalUrl') if items else None

    return {
        'statusCode': 200,
        'body': json.dumps({'originalUrl': original_url})
    }