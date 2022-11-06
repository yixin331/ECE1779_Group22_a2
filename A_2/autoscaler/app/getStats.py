from flask import request, json
from app import webapp, memcache_stat


@webapp.route('/getStats', methods=['POST'])
def getStats():
    value = {"success": "true", "content": memcache_stat}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )

    return response