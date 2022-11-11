from app import webapp, memcache, memcache_stat
from flask import request, json


@webapp.route('/listKeys', methods=['GET'])
def listKeys():
    memcache_stat['num_request'] += 1
    dataToSend = {}
    for key, item in memcache.items():
        # webapp.logger.warning(type(item.decode('utf-8')))
        dataToSend[key] = item.decode('utf-8')
    value = {"success": "true", "content": dataToSend}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )

    return response