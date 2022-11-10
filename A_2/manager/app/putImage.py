from app import webapp
from flask import request, json
import requests
import base64
import io
import random


@webapp.route('/putImage', methods=['POST'])
def putImage():
    key = request.form.get('key')
    keyToSend = {'key': key}
    try:
        response = requests.post(url='http://localhost:5002/map', data=keyToSend).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")

    node_address = 'http://' + response["content"] + ':5001/putImage'
    try:
        # call Manager app to put image
        # pass in key & file
        response = requests.post(url=node_address, data=request.form, files=request.files).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")

    return response