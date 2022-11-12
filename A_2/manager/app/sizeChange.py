from app import webapp
from flask import request, json
import requests


@webapp.route('/sizeChange', methods=['POST'])
def sizeChange():
    try:
        requests.post(url='http://localhost:5000/sizeChange', data=request.form)
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Frontend loses connection")
