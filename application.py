import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flasgger import Swagger
from flasgger.utils import swag_from
import apiFunction.api as api
import os

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = './static'

# Create an APISpec
template = {
    "info": {
        "title": "Flask Restful Swagger API doc",
        "description": "A Demof for the Flask-Restful Swagger API doc",
        "version": "0.0.1",
        "contact": {
            "name": "",
            "url": "",
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]

}
application.config['SWAGGER'] = {
    "specs_route": "/api/doc/"
}
CORS(application)
Swagger(application, template=template)


@application.route('/')
def hello_world():  # put applicationlication's code here
    return '110-DIGI-ITRI_API'


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_LANGUAGE = ['en', 'zh_TW']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@application.route('/api/photo', methods=['POST'])
@swag_from("./api_doc/photo.yml")
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files or 'language' not in request.values:
        resp = jsonify({'message': 'No file or language part in the request'})
        resp.status_code = 400
        return resp

    file = request.files['file']
    language = request.values['language']

    if file.filename == '' or language == '':
        resp = jsonify({'message': 'file and language value are required'})
        resp.status_code = 400
        return resp

    if file and allowed_file(file.filename) and language in ALLOWED_LANGUAGE:
        filename = secure_filename(file.filename)
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
        resp = api.photoAnalyze(filename=filename, language=language)
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(
            {'message': 'Allowed file types are \'png\', \'jpg\', \'jpeg\'，language are \'en\' or \'zh_TW\''})
        resp.status_code = 400
        return resp


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
