import boto3
import os
from collections import Counter
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE = "media"

def handler(event, context):
    """
    AWS Lambda function handler to process audio files uploaded to S3.
    It downloads the audio file, processes it to detect bird species,
    and saves the results back to S3.
    """
    s3_client = boto3.client('s3')

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Download the audio file from S3 to /tmp
        tmp_path = f"/tmp/{os.path.basename(key)}"
        s3_client.download_file(bucket, key, tmp_path)

        labels = []
        if key.startswith('demo-audios/'):
            # Process the audio file (this function should be defined elsewhere)
            labels = process_audio(tmp_path)
        labels_map = Counter(labels)
        table = dynamodb.Table(TABLE)

        response = table.put_item(
            Item={
                's3-url': f"https://{bucket}.s3.us-east-1.amazonaws.com/{key}",
                'tags': labels_map,
            }
        )
        print(f"Processed {key} and saved results to {response}")


def process_audio(audio_path):
    # Load and initialize the BirdNET-Analyzer models
    analyzer = Analyzer(
        classifier_model_path="model/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite",
        classifier_labels_path="model/BirdNET_GLOBAL_6K_V2.4_Labels.txt",
    )

    # Create a Recording object to process the audio file
    recording = Recording(
        analyzer,
        audio_path,
        min_conf=0.5,
    )

    # Run the analysis
    recording.analyze()

    # Collect the detected bird names
    labels = []
    for detection in recording.detections:
        labels.append(detection["common_name"])

    return labels

