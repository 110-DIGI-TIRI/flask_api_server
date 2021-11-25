from flask import jsonify
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from apiFunction.digi_jsonTrans import jsonTrans
import boto3
import os


def photoAnalyze(filename=None, language=None):
    jsonall = {"analysis_result": {}, "detail_information": {}}

    subscription_key = "af42436148d446eeb5e25f76d1e4571f"  # 洲的服務金鑰
    endpoint = "https://southcentralus.api.cognitive.microsoft.com/"  # 洲的AZ api
    images_folder = "./static/"
    local_image_path = os.path.join(images_folder, filename)

    # 驗證用戶端
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    '''
    Azure_Describe an Image - local(描述影像)----------------------------------------------------------------------------
    '''
    local_image = open(local_image_path, "rb")
    try:
        description_result = computervision_client.describe_image_in_stream(local_image)  # Call API
    except:
        jsonall["detail_information"] = None
    else:
        if len(description_result.captions) == 0:
            jsonall["detail_information"] = None
        else:
            describeMsg = {"Describe": {"confidence": round(description_result.captions[0].confidence, 4),
                                        "string": description_result.captions[0].text}}
            jsonall["detail_information"].update(describeMsg)

    '''
    AZURE、AWS Tag an Image - local(影像tag)----------------------------------------------------------------------------
    '''
    tageMsg = {"Tag": []}
    local_image = open(local_image_path, "rb")

    try:
        tags_result_local = computervision_client.tag_image_in_stream(local_image)  # Call API
    except:
        jsonall["analysis_result"].update(tageMsg)
    else:
        for tag in tags_result_local.tags:
            tageMsg["Tag"].append({"confidence": round(tag.confidence, 4), "name": tag.name})

    try:
        client = boto3.client('rekognition')

        with open(local_image_path, 'rb') as image:
            response = client.detect_labels(Image={'Bytes': image.read()})  # Call AWS API
    except:
        print("OMG")
        jsonall["analysis_result"].update(tageMsg)
    else:
        for label in response['Labels']:
            tageMsg["Tag"].append({"confidence": round(label['Confidence'] / 100, 4), "name": label['Name']})

    jsonall["analysis_result"].update(tageMsg)

    '''
    Azure Detect Color、Brands - 顏色、品牌----------------------------------------------------------------------------
    '''
    local_image = open(local_image_path, "rb")
    local_image_features = ["color", "brands"]
    color_detailMsg = {"color_detail": {"Accent color": None,
                                        "Dominant background color": None,
                                        "Dominant colors": [None],
                                        "Dominant foreground color": None,
                                        "Is black and white": None}}
    brandsMsg = {"Brands": None}
    colorMsg = {"Color": []}

    try:
        # Call API
        detect_color_results_local = computervision_client.analyze_image_in_stream(local_image, local_image_features)

    except:
        jsonall["analysis_result"].update(brandsMsg)
        jsonall["detail_information"].update(color_detailMsg)

    else:
        color_detailMsg["color_detail"]["Accent color"] = detect_color_results_local.color.accent_color

        color_detailMsg["color_detail"][
            "Dominant background color"] = detect_color_results_local.color.dominant_color_background

        color_detailMsg["color_detail"]["Dominant colors"] = detect_color_results_local.color.dominant_colors

        colorMsg["Color"] = detect_color_results_local.color.dominant_colors

        color_detailMsg["color_detail"][
            "Dominant foreground color"] = detect_color_results_local.color.dominant_color_foreground

        color_detailMsg["color_detail"]["Is black and white"] = detect_color_results_local.color.is_bw_img

        if len(detect_color_results_local.brands) > 0:
            brandsMsg["Brands"] = detect_color_results_local.brands[0].name

        jsonall["analysis_result"].update(brandsMsg)
        jsonall["analysis_result"].update(colorMsg)
        jsonall["detail_information"].update(color_detailMsg)

    if len(jsonall["analysis_result"]["Tag"]) > 0:
        jsonall.update({"message": "success"})
    else:
        jsonall.update({"message": "error"})

    if language == "zh_TW":
        zh_tw_jsonall = jsonTrans(jsonall)
        return jsonify(zh_tw_jsonall)
    else:
        return jsonify(jsonall)
