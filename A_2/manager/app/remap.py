from flask import render_template, redirect, url_for, request, json
from app import webapp, memcache_mode, node_ip
import requests
import base64
import io


@webapp.route('/remap', methods=['POST'])
def remap():
    num_node = request.form.get('num_node')

    # get all keys and images in the memcache
    key_list = {}
    for id, ip in node_ip.items():
        if not ip == None:
            try:
                node_address = 'http://' + ip + ':5001/listKeys'
                response = requests.post(url=node_address).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")
            for key, item in response["content"].items():
                key_list[key] = item

            # clear cache before remap
            try:
                node_address = 'http://' + ip + ':5001/clearCache'
                response = requests.post(url=node_address).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")

    # TODO: start/stop instances based on the num_node

    memcache_mode['num_node'] = num_node


    for key, item in key_list.items():
        try:
            keyToSend = {'key': key}
            response = requests.post(url='http://localhost:5002/map', data=keyToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Cache loses connection")

        node_address = 'http://' + response["content"] + ':5001/putImage'
        file = io.BytesIO(base64.b64decode(item))
        fileToSend = {'file': file}

        try:
            response = requests.post(url=node_address, data=keyToSend, files=fileToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Cache loses connection")
        if response is None or response["success"] == "false":
            webapp.logger.warning("Key: " + str(key) + "cannot remap to cache")

    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response