import os
import sys
import glob
from typing import Dict
from dotenv import dotenv_values

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient

# from bo

CFG = dotenv_values()

# Add endpoint and keyword
endpoint = CFG["AZURE_FORM_RECOGNIZER_ENDPOINT"]
key = CFG["AZURE_FORM_RECOGNIZER_KEY"]

# Import form regconizer modules
form_recognizer_client = FormRecognizerClient(endpoint=endpoint,
                                              credential=AzureKeyCredential(key))


def get_information(
        file,
        collected_fields=["FirstName", "LastName", "DocumentNumber", "DateOfBirth", "Sex"]
) -> Dict[str, str]:
    id_content = form_recognizer_client.begin_recognize_identity_documents(identity_document=file)
    identity_card = id_content.result()
    identity_card = identity_card[0]
    info_dict = {}
    for f in collected_fields:
        item = identity_card.fields.get(f)
        print("{}: {} has confidence: {}".format(f, item.value, item.confidence))
        info_dict[f] = item.value
    return info_dict


if __name__ == "__main__":
    files = glob.glob("material_preparation_step/digital_id_template/ca-dl*.png")
    files = [f for f in files if not ("sample" in os.path.basename(f) or ("template" in os.path.basename(f)))]
    info_list = []
    for i, file in enumerate(files, start=1):
        print("-"*10)
        print("{}/{} Extracting information from: {}".format(i, len(files), file))
        with open(file, "rb") as f:
            info_dict = get_information(file=f)
        info_list.append(info_dict)
        break

