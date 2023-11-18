import io
import datetime
import pandas as pd
from PIL import Image
import requests
import io
import glob, os, sys, time, uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from matplotlib.pyplot import imshow
import matplotlib.pyplot as plt

from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw

from video_indexer import VideoIndexer
from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from msrest.authentication import CognitiveServicesCredentials

from dotenv import dotenv_values

CFG = dotenv_values()

video_analysis = VideoIndexer(
    vi_subscription_key=CFG['SUBSCRIPTION_KEY'],
    vi_location=CFG['LOCATION'],
    vi_account_id=CFG['ACCOUNT_ID']
)

video_analysis.check_access_token()

face_client = FaceClient(CFG["AZURE_FACEAPI_ENDPOINT"],
                         CognitiveServicesCredentials(CFG["AZURE_FACEAPI_KEY"]))


def upload_video(filepath):
    upload_video_id = video_analysis.upload_to_video_indexer(
        input_filename=filepath, video_name="sample-video"
    )
    return upload_video_id


def get_info(video_id):
    info = video_analysis.get_video_info(video_id, video_language='English')
    return info


def extract_face_thumbnails(info, save_image=False):
    if len(info['videos'][0]['insights']['faces'][0]['thumbnails']):
        print("We found {} faces in this video.".format(str(len(info['videos'][0]['insights']['faces'][0]['thumbnails']))))
    # Get thumnail ID from Analysis JSON
    images = []
    img_raw = []
    img_strs = []
    for each_thumb in info['videos'][0]['insights']['faces'][0]['thumbnails']:
        if 'fileName' in each_thumb and 'id' in each_thumb:
            file_name = each_thumb['fileName']
            thumb_id = each_thumb['id']
            img_code = video_analysis.get_thumbnail_from_video_indexer(
                video_id,  thumb_id
            )
            img_strs.append(img_code)
            img_stream = io.BytesIO(img_code)
            img_raw.append(img_stream)
            img = Image.open(img_stream)
            if save_image:
                img.save("".join(["step_3/", file_name, ".jpeg"]))
            images.append(img)
    return images


def show_image(images):
    for img in images:
        print(img.info)
        plt.figure()
        plt.imshow(img)


def build_person_group(filepath, pgp_name):
    print('Create and build a person group...')
    # Create empty Person Group.
    # Person Group ID must be lower case, alphanumeric, and/or with '-', '_'.
    person_group_id = str(uuid.uuid4())
    print('Person group ID:', person_group_id)
    face_client.person_group.create(
        person_group_id=person_group_id, name=person_group_id
    )

    # Create a person group person.
    my_face = face_client.person_group_person.create(
        person_group_id=person_group_id, name=pgp_name
    )

    # Find all jpeg images of human in working directory.
    my_face_images = [file for file in glob.glob(filepath)]
    print(my_face_images)
    # Add images to a Person object
    for image_p in my_face_images:
        with open(image_p, 'rb') as w:
            face_client.person_group_person.add_face_from_stream(
                person_group_id, my_face.person_id, w
            )

    # Train the person group, after a Person object with many images were added to it.
    face_client.person_group.train(person_group_id)
    # Wait for training to finish.
    while (True):
        training_status = face_client.person_group.get_training_status(person_group_id)
        print("Training status: {}.".format(training_status.status))
        if (training_status.status is TrainingStatusType.succeeded):
            break
        elif (training_status.status is TrainingStatusType.failed):
            face_client.person_group.delete(person_group_id)
            sys.exit('Training the person group has failed.')
        time.sleep(5)
    return face_client, person_group_id


def detect_faces(face_client, query_images_path):
    print('Detecting faces in query images list...')

    # Keep track of the image ID and the related image in a dictionary
    face_ids = {}
    query_images_list = glob.glob(query_images_path)
    for image_name in query_images_list:
        
        print("Opening image: ", image_name)
        time.sleep(5)
        img_name =  os.path.splitext(os.path.basename(image_name))[0]
        # Detect the faces in the query images list one at a time
        faces = extract_face_one_image(face_client, image_name)

        # Add all detected face IDs to a list
        for face in faces:
            print('Face ID', face.face_id, 'found in image',img_name + '.jpg')
            # Add the ID to a dictionary with image name as a key.
            # This assumes there is only one face per image (since you can't have duplicate keys)
            face_ids[img_name] = face.face_id

    return face_ids


def extract_face_one_image(face_client, face_path, local=True):
    """
    Args: face_path: could be a local path or url

    Returns: dl_faces: face & id
    """

    if local:
        dl_image = open(face_path, 'rb')
        # Detect the faces in the images
        dl_faces = face_client.face.detect_with_stream(dl_image)
    else:
        dl_faces = face_client.face.detect_with_url(face_path)
    return dl_faces


def verify_face_id(face_client, dl_faces, dl_ref_face):
    """
    Agrs: ref_face: face extracted from the ID card
    """
    face_verify_results = []
    if dl_ref_face:
        for face in dl_faces:
            verify_result = face_client.face.verify_face_to_face(
                face.face_id, dl_ref_face[0].face_id
            )
            if verify_result.is_identical:
                verify = "Positive"
            else:
                verify = "Negative"
            face_verify_results.append(
                {"dl_face_id": face.face_id, "verify": verify,
                 "confidence": verify_result.confidence})
    return face_verify_results

def verify_id_personal_model(face_client, face_id, person_group_id):
    person_gp_results = face_client.face.identify([face_id], person_group_id)
    return person_gp_results

def extract_sentiment():
    


def show_image_in_cell(face_url, img_path=None):
    if img_path:
        img = Image.open(img_path)
    else:
        response = requests.get(face_url)
        img = Image.open(BytesIO(response.content))
    plt.figure(figsize=(10,5))
    plt.imshow(img)
    plt.show()


if __name__ == "__main__":
    # ----------- Upload video ----------- 
    # filepath = 'digital-video-sample/avkash-boarding-pass.mp4'
    # upload_video_id = upload_video(filepath)
    # print(upload_video_id)

    # -----------  Extract face thumbnail ----------- 
    # video_id = "ba881bbe51"
    # info = get_info(video_id)
    # images = extract_face_thumbnails(info)

    # -----------  Create person model ----------- 
    single_face = "https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg"
    selected_image = single_face
    person_group_name = "test"
    training_path = "step_3/training_face/*.jpg"
    face_client, person_group_id = build_person_group(pgp_name=person_group_name, filepath=training_path)
    test_path = "step_3/test_face/*.jpeg"
    ids = detect_faces(face_client, test_path)
    print(ids)
    
    # -----------  Face verification ----------- 
    person_group_id = "dca98aa7-419c-4039-8813-18a7f55ddb15"
    face_client.personal_group.get(person_group_id)

    # -----------  Extract sentimental ----------- 
    person_group_id = "dca98aa7-419c-4039-8813-18a7f55ddb15"
    