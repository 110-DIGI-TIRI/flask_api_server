from flask import jsonify


def photoAnalyze(filename=None, language=None):
    msg = None
    if language == 'en':
        msg = {
            "message": "success",
            "analysis_result": {
                "Brands": "New Balance",
                "Color": ['White', 'Red'],
                "Tag": [
                    {
                        "name": "shoe",
                        "confidence": 0.9849
                    },
                    {
                        "name": "walking shoe",
                        "confidence": 0.9646
                    },
                    {
                        "name": "sneakers",
                        "confidence": 0.9623
                    },
                    {
                        "name": "shoe",
                        "confidence": 0.9999
                    },
                    {
                        "name": "Clothing",
                        "confidence": 0.9999
                    },
                    {
                        "name": "Footwear",
                        "confidence": 0.9999
                    }
                ]
            },
            "detail_information": {
                "Describe": {
                    "string": "a red and white shoe",
                    "confidence": 0.4932
                },
                "color_detail": {
                    "Is black and white": False,
                    "Accent color": "#862425",
                    "Dominant background color": "White",
                    "Dominant foreground color": "White",
                    "Dominant colors": ['White', 'Red']
                }
            }
        }
    elif language == 'zh_TW':
        msg = {
            "message": "success",
            "analysis_result": {
                "Brands": "New Balance",
                "Color": ['白', '紅'],
                "Tag": [
                    {
                        "name": "鞋",
                        "confidence": 0.9849
                    },
                    {
                        "name": "步行鞋",
                        "confidence": 0.9646
                    },
                    {
                        "name": "運動鞋",
                        "confidence": 0.9623
                    },
                    {
                        "name": "鞋",
                        "confidence": 0.9999
                    },
                    {
                        "name": "衣服",
                        "confidence": 0.9999
                    },
                    {
                        "name": "鞋類",
                        "confidence": 0.9999
                    }
                ]
            },
            "detail_information": {
                "Describe": {
                    "string": "一隻紅白相間的鞋子",
                    "confidence": 0.4932
                },
                "color_detail": {
                    "Is black and white": False,
                    "Accent color": "#862425",
                    "Dominant background color": "白",
                    "Dominant foreground color": "白",
                    "Dominant colors": ['白', '紅']
                }
            }
        }

    return jsonify(msg)
