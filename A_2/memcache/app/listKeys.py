from app import webapp, memcache
from flask import request, json


@webapp.route('/listKeys', methods=['GET'])
def listKeys():
    value = {"success": "true", "content": memcache}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )

    return response