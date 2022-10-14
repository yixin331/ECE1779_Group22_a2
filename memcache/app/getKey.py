from app import webapp, memcache, memcache_stat, memcache_config
from flask import request, json

@webapp.route('/getKey', methods=['POST'])
def getKey():
    memcache_stat['num_request'] += 1
    memcache_stat['num_get'] += 1
    key = request.form.get('key')

    if key in memcache:
        if memcache_config['policy'] == "LRU":
            memcache.move_to_end(key)
        value = {"success": "true", "content": memcache[key].decode('utf-8'), "message": "Get from cache"}
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
    else:
        # unknown key
        memcache_stat['num_miss'] += 1
        value = {"success": "false", "error": {"code": 400, "message": "Key does not exist"}}
        response = webapp.response_class(
                response=json.dumps(value),
                status=400,
                mimetype='application/json'
        )

    return response