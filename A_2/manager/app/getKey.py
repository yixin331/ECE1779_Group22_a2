from app import webapp
from flask import request, json
import requests


@webapp.route('/getKey', methods=['POST'])
def getKey():
    response = None
    try:
        response = requests.post(url='http://localhost:5001/getKey', data=request.form).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")

    return response