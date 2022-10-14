from app import webapp, memcache, num_request, policy, capacity, num_item, total_size
from flask import request, json
import base64
import io
import random


@webapp.route('/putImage', methods=['POST'])
def putImage():
    global num_request
    global capacity
    global num_item
    global total_size
    num_request += 1
    key = request.form.get('key')
    if 'file' not in request.files:
        value = {"success": "false", "error": {"code": 400, "message": "Please pass a file"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=400,
            mimetype='application/json'
        )
        return  response
    file = request.files['file']

    file.seek(0, 2)  # seeks the end of the file
    item_size = file.tell()  # tell at which byte we are
    file.seek(0, 0)  # go back to the beginning of the file

    if item_size > capacity * 1024 * 1024:
        # image is too large
        value = {"success": "false", "error": {"code": 400, "message": "Image is too large to put into cache"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=400,
            mimetype='application/json'
        )
        return response

    if key in memcache:
        invalidate_key(key)

    free_cache(item_size)

    # add image into cache
    num_item += 1
    total_size += item_size
    webapp.logger.warning(total_size)
    image_string = base64.b64encode(file.read())
    memcache[key] = image_string

    if policy == "LRU":
        memcache.move_to_end(key)

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
    while item_size + total_size > capacity * 1024 * 1024:
        if policy == "LRU":
            item_to_remove = io.BytesIO(base64.b64decode(memcache.popitem(last=False)))
        else:
            item_to_remove = io.BytesIO(base64.b64decode(memcache.pop(random.choice(memcache.keys()))))
        num_item -= 1

        item_to_remove.seek(0, 2)  # seeks the end of the file
        item_to_remove_size = item_to_remove.tell()  # tell at which byte we are
        item_to_remove.seek(0, 0)  # go back to the beginning of the file

        total_size -= item_to_remove_size


def invalidate_key(key):
    global num_request
    global num_item
    global total_size
    num_request += 1
    if key in memcache:
        item_to_remove = io.BytesIO(base64.b64decode(memcache.pop(key)))
        num_item -= 1

        item_to_remove.seek(0, 2)  # seeks the end of the file
        item_to_remove_size = item_to_remove.tell()  # tell at which byte we are
        item_to_remove.seek(0, 0)  # go back to the beginning of the file

        total_size -= item_to_remove_size
        return 1
    else:
        return -1