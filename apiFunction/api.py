from flask import jsonify


def photoAnalyze(filename=None):
    msg = {
        "message": "success",
        "analysis_result": {
            "azure": {
                "Brands": "New Balance",
                "Color": ['White', 'Red'],
                "Tag": {
                    "0": {
                        "name": "shoe",
                        "confidence": 0.9849
                    },
                    "1": {
                        "name": "walking shoe",
                        "confidence": 0.9646
                    },
                    "2": {
                        "name": "sneakers",
                        "confidence": 0.9623
                    }
                }
            },
            "aws": {
                "Tag": {
                    "0": {
                        "name": "shoe",
                        "confidence": 99.99983978271484
                    },
                    "1": {
                        "name": "Clothing",
                        "confidence": 99.99983978271484
                    },
                    "2": {
                        "name": "Footwear",
                        "confidence": 99.99983978271484
                    }
                }
            }
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

    return jsonify(msg)
