import os
import sys

from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential

from dotenv import dotenv_values

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

CFG = dotenv_values()
endpoint = CFG["AZURE_FORM_RECOGNIZER_ENDPOINT"]
key = CFG["AZURE_FORM_RECOGNIZER_KEY"]


trainingDataUrl = CFG["BP_TRAINING_URL"]
testDataUrl = CFG["BP_TEST_URL"]
form_training_client = FormTrainingClient(endpoint=endpoint,
                                          credential=AzureKeyCredential(key))
form_recognize_client = FormRecognizerClient(endpoint=endpoint,
                                             credential=AzureKeyCredential(key))


def training_boarding_pass(trainingDataUrl):
    labeled_training_process = form_training_client.begin_training(
        trainingDataUrl, use_training_labels=True)
    labeled_custom_model = labeled_training_process.result()
    return labeled_custom_model


def infer_boarding_pass_from_url(model_id, testDataUrl):
    result = form_recognize_client.begin_recognize_custom_forms_from_url(
        model_id=model_id, form_url=testDataUrl
    )
    return result


def show_training_result(training_model):
    while training_model.status != "ready":
        print(training_model.status)
    else:
        for doc in training_model.training_documents:
            print("Document name: {}".format(doc.name))
            print("Document status: {}".format(doc.status))
            print("Document page count: {}".format(doc.page_count))
            print("Document errors: {}".format(doc.errors))


def infer_boarding_pass_from_file(model_id, file_path):
    with open(file_path, "rb") as f:
        test_action = form_recognize_client.begin_recognize_custom_forms(
            model_id=model_id, form=f
        )

    return test_action


def show_test_result(test_action):
    while test_action.status() == "InProgress":
        print(test_action.status())
    else:
        test_action_result = test_action.result()
        for recognized_content in test_action_result:
            print("Form type: {}".format(recognized_content.form_type))
            boarding_pass_dict = {}
            for name, field in recognized_content.fields.items():
                value = remove_duplicate_str(field.value)
                print("Field '{}' has label '{}' with value '{}' "
                      "and a confidence score of {}".format(
                       name,
                       field.label_data.text if field.label_data else name,
                       value,
                       field.confidence))
                boarding_pass_dict[name] = value
    return boarding_pass_dict


def remove_duplicate_str(value):
    if isinstance(value, str):
        x = value.split()
        value = " ".join(sorted(set(x), key=x.index))
    return value


if __name__ == "__main__":
    # ========================TRAINING_CUSTOM_FORM_MODEL========================
    # labeled_custom_model = training_boarding_pass(trainingDataUrl)
    # print("Model ID:", labeled_custom_model.model_id)
    # show_training_result(labeled_custom_model)
    # ========================TEST_CUSTOM_FORM_MODEL========================
    model_id = "23da12e2-3d71-4ce6-86dc-18095d271748"
    # Test file from URL 
    # test_action = infer_boarding_pass_from_url(model_id, testDataUrl)
    # Or local file
    file_path = "material_preparation_step/boarding_pass_template/boarding-anh.pdf"
    test_action = infer_boarding_pass_from_file(model_id, file_path)
    boarding_pass_dict = show_test_result(test_action)
    print(boarding_pass_dict)