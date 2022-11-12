from app import webapp
from flask import request, json
import requests


@webapp.route('/sizeChange', methods=['POST'])
def sizeChange():
    try:
        webapp.logger.warning('size change from autoscaler')
        requests.post(url='http://localhost:5000/sizeChange', data=request.form)
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Frontend loses connection")
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response
