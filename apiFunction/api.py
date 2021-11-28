from flask import jsonify
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from apiFunction.digi_jsonTrans import jsonTrans

import apiFunction.webCrawlerFunction as wcf
import boto3
import os
import time
import matplotlib.pyplot as plt


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


def crawler(keyword):
    start = time.time()
    # 爬蟲資料統整
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    # keyword = '鍵盤'
    pages = 2

    start = time.time()
    df_pchome = wcf.PChome(headers, keyword, pages)
    df_momo = wcf.momo(headers, keyword, pages)
    # 計時終點
    end = time.time()
    # print("程式花費的時間：", format(end - start))

    # =============================================================================
    # 整理csv檔/pchome and momo
    # df_keyboard_pchome=tidyDfandgetPrice('mom.csv') #收到的pchome csv檔
    # df_keyboard_momo=momoShoptidyDfandgetPrice('k.csv') #收到的momo csv檔
    # df_pchome = wcf.tidyDfandgetPrice('PChome.csv')  # 收到的pchome csv檔
    # df_momo = wcf.momoShoptidyDfandgetPrice('momo.csv')  # 收到的momo csv檔
    df_pchome = wcf.tidyDfandgetPrice(df_pchome)  # 收到的pchome csv檔
    df_momo = wcf.momoShoptidyDfandgetPrice(df_momo)  # 收到的momo csv檔
    df = df_pchome.append(df_momo)  # 兩個電商的相加

    df_excludeCombine = wcf.getnotCombineProduct(df)  # 排除組合價
    keyboard_q1, keyboard_q3, df_excludeoutlier = wcf.deleteExcludeOutlierPrice(df_excludeCombine)  # 計算四分位並排除outlier

    # print('鍵盤主要價格:${}$-${}'.format(int(keyboard_q1), int(keyboard_q3)))

    # 取正常售價並根據價格,折扣數來排序
    df_keyboard_sortincrease_byprice, df_keyboard_sortdecrease_byprice = wcf.sortNormalProductbyPrice(df_excludeoutlier,
                                                                                                      keyboard_q1,
                                                                                                      keyboard_q3)

    # 取推薦商品
    df_lowestbyprice = wcf.getLowestPrice(df_keyboard_sortincrease_byprice)  # 價格最低
    df_lowestbydiscountpercent = wcf.getLowestDiscountpercent(df_keyboard_sortincrease_byprice)  # 折扣最多

    # 轉成json檔
    js_price_decrease = wcf.dataframeTransfertoJson(df_keyboard_sortdecrease_byprice)
    js_price_increase = wcf.dataframeTransfertoJson(df_keyboard_sortincrease_byprice)
    js_recommand_lowest = wcf.dataframeTransfertoJson(df_lowestbyprice)
    js_recommand_discount = wcf.dataframeTransfertoJson(df_lowestbydiscountpercent)

    # 組成json格式
    alljson = '{' + '"normalPrice25":' + str(
        keyboard_q3) + ',"narmalPrice75":' + str(
        keyboard_q1) + ',' + '"table_normal_decrease":' + js_price_decrease + ',' + '"table_normal_increase":' + js_price_increase + ',' + '"table_recommand_lowest":' + js_recommand_lowest + ',' + '"table_recommand_discount":' + js_recommand_discount + '}'
    return alljson
