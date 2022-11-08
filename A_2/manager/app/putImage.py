from app import webapp
from flask import request, json
import requests
import base64
import io
import random


@webapp.route('/putImage', methods=['POST'])
def putImage():
    try:
        # call Manager app to put image
        # pass in key & file
        response = requests.post(url='http://localhost:5001/putImage', data=request.form, files=request.files).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")
    return response