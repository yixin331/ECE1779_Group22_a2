from app import webapp, memcache, memcache_stat
from flask import request, json


@webapp.route('/clearCache', methods=['POST'])
def clearCache():
    memcache_stat['num_request'] += 1
    memcache_stat['num_item'] = 0
    memcache_stat['total_size'] = 0
    memcache.clear()
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


@webapp.route('/clearStats', methods=['POST'])
def clearStats():
    memcache_stat['num_request'] = 0
    memcache_stat['num_item'] = 0
    memcache_stat['total_size'] = 0
    memcache_stat['num_get'] = 0
    memcache_stat['num_miss'] = 0
    memcache.clear()
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response