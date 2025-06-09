import os
import boto3

def get_s3_client():
    """
    Create and return an S3 client using boto3.
    """
    return boto3.client('s3')


def get_dynamodb_table():
    """
    Return a DynamoDB Table resource for the configured table name.
    """
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(os.environ['DDB_TABLE'])


def get_bucket_names():
    """
    Retrieve the raw and thumbnail bucket names from environment variables.
    """
    return os.environ['RAW_BUCKET'], os.environ['THUMB_BUCKET']


def invoke_model(bucket, key):
    """
    Invoke a pretrained model to detect bird species within a file.
    Placeholder: implement actual model invocation logic.
    Returns a dictionary mapping species to counts, e.g., {"crow": 2}.
    """
    # TODO: integrate with SageMaker endpoint or local model
    return {"crow": 2}

def invoke_model_file(file_content):
    """
    Invoke a pretrained model to detect bird species from raw file content.
    Placeholder: implement actual model invocation logic.
    Returns a dict mapping species to counts, e.g., {"crow": 1}.
    """
    # TODO: decode file_content and call model endpoint
    return {"crow": 1}
