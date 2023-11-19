import requests
import time 
import matplotlib.pyplot as plt 
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
import os, time, uuid

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
from dotenv import dotenv_values

TRAINING_ENDPOINT = "ENTER TRAINING ENDPOINT HERE"
training_key = "ENTER TRAINING RESOURCE KEY HERE"
training_resource_id = 'ENTER TRAINING RESOURCE ID HERE'

PREDICTION_ENDPOINT = 'ENTER PREDICTION RESOURCE KEY HERE'
prediction_key = "ENTER PREDICTION RESOURCE KEY HERE"
prediction_resource_id = "ENTER PREDICTION RESOURCE ID HERE"

# Instantiate and authenticate the training client with endpoint and key
training_credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(TRAINING_ENDPOINT, training_credentials)

# Instantiate and authenticate the prediction client with endpoint and key
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(PREDICTION_ENDPOINT, prediction_credentials)


def show_image_in_cell(img_url):
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    plt.figure(figsize=(20,10))
    plt.imshow(img)
    plt.show()


def train_model(project_id):
    iter = trainer.train_project(project_id)
    while (iter.status != "Complete"):
        iter = trainer.get_iteration(project_id, iter.id)
        print("training_status:" + iter.status)
        print("waiting for 10 sec")
        time.sleep(10)
    return iter.as_dict()


def publish_model(publish_iteration_name, iter):
    # The iteration is now trained. Publish it to the project endpoint
    trainer.publish_iteration(project.id, iter.id,
                              publish_iteration_name,
                              prediction_resource_id)
    print("Done!")


def perform_prediction(image_file_name):

    with open(os.path.join(local_image_path,  image_file_name), "rb") as image_contents:
        results = predictor.detect_image(project.id, publish_iteration_name, image_contents.read())
        # Display the results.
        for prediction in results.predictions:
            print("\t" + prediction.tag_name +
                  ": {0:.2f}%".format(prediction.probability * 100)) 


if __name__ == "__main__":
    # Find the object detection domain
    obj_detection_domain = next(domain for domain in trainer.get_domains() if domain.type == "ObjectDetection" and domain.name == "General")
    # Create a new project
    print ("Your Object Detection Training project has been created. Please move on.")
    project_name = uuid.uuid4()
    project = trainer.create_project(project_name, domain_id=obj_detection_domain.id)