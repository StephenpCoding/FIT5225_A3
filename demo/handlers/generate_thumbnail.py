import os
import boto3
import cv2
import numpy as np
from aws_helpers import get_s3_client, get_bucket_names

def lambda_handler(event, context):
    # Create S3 client and get bucket names
    s3 = get_s3_client()
    raw_bucket, thumb_bucket = get_bucket_names()

    # Process each record in the S3 event
    for record in event['Records']:
        key = record['s3']['object']['key']
        download_path = f"/tmp/{key.replace('/', '_')}"
        thumb_key = key.rsplit('.', 1)[0] + '-thumb.jpg'

        # Download the original image from S3
        s3.download_file(raw_bucket, key, download_path)

        # Read image and compute thumbnail dimensions
        img = cv2.imread(download_path)
        h, w = img.shape[:2]
        new_w = 200
        new_h = int(h * (new_w / w))
        thumb = cv2.resize(img, (new_w, new_h))

        # Save thumbnail locally and upload to S3
        thumb_path = f"/tmp/{thumb_key.replace('/', '_')}"
        cv2.imwrite(thumb_path, thumb)
        s3.upload_file(thumb_path, thumb_bucket, thumb_key)

    return {'statusCode': 200, 'body': 'Thumbnails generated successfully'}
