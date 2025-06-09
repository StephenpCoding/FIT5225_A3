
from ultralytics import YOLO
import supervision as sv
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os
import requests
import boto3
import sys
from collections import Counter

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE = "media"

def handle(event,context):
  def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        image_path = f"/tmp/{key.split('/')[-1]}"
        s3_client.download_file(bucket, key, image_path)

        labels = []
        if key.startswith('images/'):
          labels = image_prediction(image_path)
          b = create_thumbnail(image_path)
          s3_client.put_object(
          Bucket=bucket,
          Key=f"thumbnails/{key.split('/')[-1]}",
          Body=b,
          ContentType='image/png',            
          ContentDisposition='inline'
          )
        elif key.startswith('videos/'):
          labels = video_prediction(image_path)
        else:
          print(f"Unsupported file type for key: {key}")

        labels_map = Counter(labels)

        try:
          dynamodb.Table(TABLE).put_item(
              Item = {
                  's3-url': f"https://{bucket}.s3.us-east-1.amazonaws.com/{key}",
                  'tags' : labels_map, 
              }
          )

        except boto3.ClientError as err:
          print(f"Error saving to DynamoDB: {err}")
        except Exception as e:
          print(f"An unexpected error occurred: {e}")

def create_thumbnail(image_path, width=150, height=150):

    _ , ext = os.path.splitext(image_path)[-1]

    img = cv.imread(image_path)
    if img is None:
        print("Couldn't load the image! Please check the image path.")
        return None

    # Resize to thumbnail dimensions
    thumbnail = cv.resize(img, (width, height))

    # Encode the thumbnail to PNG in memory and return the bytes
    ok, buffer = cv.imencode(ext, thumbnail)
    if not ok:
        print("Error encoding the image.")
        return None

    return buffer.tobytes()




def image_prediction(image_path,  confidence=0.5, model="./model.pt"):

    # Load YOLO model
    model = YOLO(model)
    class_dict = model.names

    # Load image from local path
    img = cv.imread(image_path)

    # Check if image was loaded successfully
    if img is None:
        print("Couldn't load the image! Please check the image path.")
        return

    # Run the model on the image
    result = model(img)[0]

    # Convert YOLO result to Detections format
    detections = sv.Detections.from_ultralytics(result)

    # Filter detections based on confidence threshold and check if any exist
    if detections.class_id is not None:
        detections = detections[(detections.confidence > confidence)]

        # Create labels for the detected objects
        labels = [f"{class_dict[cls_id]}" for cls_id in 
                  detections.class_id]

    return labels


# ## Video Detection
def video_prediction(video_path, result_filename=None, save_dir = "./video_prediction_results", confidence=0.5, model="./model.pt"):

    labels = []
    try:
        # Load video info and extract width, height, and frames per second (fps)
        video_info = sv.VideoInfo.from_video_path(video_path=video_path)
        fps = int(video_info.fps)

        model = YOLO(model)  # Load your custom-trained YOLO model
        tracker = sv.ByteTrack(frame_rate=fps)  # Initialize the tracker with the video's frame rate
        class_dict = model.names  # Get the class labels from the model

        
        # Capture the video from the given path
        cap = cv.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error: couldn't open the video!")

        # Process the video frame by frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:  # End of the video
                break

            # Make predictions on the current frame using the YOLO model
            result = model(frame)[0]
            detections = sv.Detections.from_ultralytics(result)  # Convert model output to Detections format
            detections = tracker.update_with_detections(detections=detections)  # Track detected objects

            # Filter detections based on confidence
            if detections.tracker_id is not None:
                detections = detections[(detections.confidence > confidence)]  # Keep detections with confidence greater than a threashold

                labels_1 = [f"{class_dict[cls_id]}" for cls_id in 
                            detections.class_id]
                labels.extend(labels_1)
        return labels


    except Exception as e:
        print(f"An error occurred: {e}")
        return labels
    
    finally:
        # Release resources
        cap.release()
        print("Video processing complete, Released resources.")



if __name__ == '__main__':
    print("predicting...")
    print(image_prediction("./test_images/crows_1.jpg"))
    print(video_prediction("./test_videos/crows.mp4",result_filename='crows_detected.mp4'))
