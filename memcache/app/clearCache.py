from app import webapp, memcache, num_request, num_item, total_size
from flask import request, json


@webapp.route('/clearCache', methods=['POST'])
def clearCache():
    global num_request
    global num_item
    global total_size
    num_request += 1
    num_item = 0
    total_size = 0
    memcache.clear()
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response