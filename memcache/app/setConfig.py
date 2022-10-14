from app import webapp, memcache, policy, capacity, total_size, num_item, dbconnection
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
    global capacity
    policy = request.form['policy']
    capacity = int(request.form['size'])
    dbconnection.put_config(capacity, policy)
    free_cache(0)
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


def free_cache(item_size):
    global total_size
    global capacity
    global num_item
    # remove items until the new image can fit into the cache
    while item_size + total_size > int(capacity) * 1024 * 1024:
        if policy == "LRU":
            item_to_remove = io.BytesIO(base64.b64decode(memcache.popitem(last=False)))
        else:
            item_to_remove = io.BytesIO(base64.b64decode(memcache.pop(random.choice(memcache.keys()))))
        num_item -= 1

        item_to_remove.seek(0, 2)  # seeks the end of the file
        item_to_remove_size = item_to_remove.tell()  # tell at which byte we are
        item_to_remove.seek(0, 0)  # go back to the beginning of the file

        total_size -= item_to_remove_size