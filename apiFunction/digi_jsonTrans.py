import googletrans


def jsonTrans(analyzeJson=None):
    """
    JSON資料轉中文
    :param analyzeJson: 分析後的JSON檔案(dic型態)
    :return: 翻譯後的JSON檔案
    """
    # Initial
    translator = googletrans.Translator()

    zh_tw_JSON = analyzeJson.copy()  # 深度複製
    zh_tw_colorList = []

    for firstLayerKey, f_subLayerValue in analyzeJson.items():
        # analysis_result的翻譯
        if firstLayerKey == "analysis_result":
            for secondLayerKey, s_subLayerValue in f_subLayerValue.items():
                # Color的翻譯
                if secondLayerKey == "Color":
                    for transColor in s_subLayerValue:
                        try:
                            zh_CN_results = translator.translate(transColor, dest='zh-TW')
                        except:
                            zh_tw_colorList.append(transColor)
                        else:
                            zh_tw_colorList.append(zh_CN_results.text.replace("的", ""))

                    zh_tw_JSON[firstLayerKey][secondLayerKey] = zh_tw_colorList

                # Tag的翻譯，enumerate取list的index、value
                if secondLayerKey == "Tag":
                    for tagListIndex, tagListValue in enumerate(s_subLayerValue):
                        try:
                            zh_CN_results = translator.translate(tagListValue["name"], dest='zh-tw')
                        except:
                            continue
                        else:
                            zh_tw_JSON[firstLayerKey][secondLayerKey][tagListIndex]["name"] = zh_CN_results.text
        # detail_information的翻譯
        if firstLayerKey == "detail_information":
            # Describe的翻譯
            try:
                zh_CN_results = translator.translate(f_subLayerValue["Describe"]["string"], dest='zh-tw')
            except:
                continue
            else:
                zh_tw_JSON[firstLayerKey]["Describe"]["string"] = zh_CN_results.text

            # color_detail的翻譯
            # Dominant background color、Dominant foreground color的翻譯
            try:
                zh_CN_results_background = translator.translate(
                    f_subLayerValue["color_detail"]["Dominant background color"], dest='zh-tw')
                zh_CN_results_foreground = translator.translate(
                    f_subLayerValue["color_detail"]["Dominant foreground color"], dest='zh-tw')
            except:
                continue
            else:
                zh_tw_JSON[firstLayerKey]["color_detail"][
                    "Dominant background color"] = zh_CN_results_background.text.replace("的", "")
                zh_tw_JSON[firstLayerKey]["color_detail"][
                    "Dominant foreground color"] = zh_CN_results_foreground.text.replace("的", "")

            # Dominant colors的翻譯
            zh_tw_JSON[firstLayerKey]["color_detail"]["Dominant colors"] = zh_tw_colorList

    return zh_tw_JSON
