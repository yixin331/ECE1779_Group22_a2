from app import webapp, memcache, memcache_stat, memcache_config
from flask import request, json
import base64
import io
import random


@webapp.route('/putImage', methods=['POST'])
def putImage():
    memcache_stat['num_request'] += 1
    key = request.form.get('key')
    file = request.files['file']

    file.seek(0, 2)  # seeks the end of the file
    item_size = file.tell()  # tell at which byte we are
    file.seek(0, 0)  # go back to the beginning of the file
    webapp.logger.warning(item_size)

    if item_size > memcache_config['capacity'] * 1024 * 1024:
        # image is too large
        value = {"success": "false", "error": {"code": 413, "message": "Image is too large to put into cache"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=413,
            mimetype='application/json'
        )
        return response

    if key in memcache:
        invalidate_key(key)

    free_cache(item_size)

    # add image into cache
    memcache_stat['num_item'] += 1
    memcache_stat['total_size'] += item_size
    webapp.logger.warning(memcache_stat['total_size'])
    memcache[key] = base64.b64encode(file.read())

    memcache.move_to_end(key)

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


def invalidate_key(key):
    if key in memcache:
        item_to_remove = io.BytesIO(base64.b64decode(memcache.pop(key)))
        memcache_stat['num_item'] -= 1

        item_to_remove.seek(0, 2)  # seeks the end of the file
        item_to_remove_size = item_to_remove.tell()  # tell at which byte we are
        item_to_remove.seek(0, 0)  # go back to the beginning of the file

        memcache_stat['total_size'] -= item_to_remove_size
        return 1
    else:
        return -1
