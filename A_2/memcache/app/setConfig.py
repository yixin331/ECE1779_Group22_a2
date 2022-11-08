from app import webapp, memcache, memcache_config, memcache_stat
from flask import request, json, g
import base64
import io
import random


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/setConfig', methods=['POST'])
def setConfig():
    memcache_stat['num_request'] += 1
    memcache_config['policy'] = request.form['policy']
    memcache_config['capacity'] = int(request.form['size'])
    # dbconnection.put_config(memcache_config['capacity'], memcache_config['policy'])
    free_cache(0)
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


def free_cache(item_size):
    # remove items until the new image can fit into the cache
    while item_size + memcache_stat['total_size'] > memcache_config['capacity'] * 1024 * 1024:
        if memcache_config['policy'] == "LRU":
            item_to_remove = io.BytesIO(base64.b64decode(memcache.popitem(last=False)[1]))
        else:
            item_to_remove = io.BytesIO(base64.b64decode(memcache.pop(random.choice(list(memcache.keys())))))
        memcache_stat['num_item'] -= 1

        item_to_remove.seek(0, 2)  # seeks the end of the file
        item_to_remove_size = item_to_remove.tell()  # tell at which byte we are
        item_to_remove.seek(0, 0)  # go back to the beginning of the file

        memcache_stat['total_size'] -= item_to_remove_size