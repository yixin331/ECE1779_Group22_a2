from flask import render_template, redirect, url_for, request, json
from app import webapp, memcache_mode, node_ip, config, memcache_config, dbconnection
from app.config import aws_config
import requests
import base64
import io
import boto3
import time


def schedule_cloud_watch(ip, id):
    try:
        node_address = 'http://' + str(ip) + ':5001/putStat'
        idToSend = {'InstanceId': id}
        response = requests.post(url=node_address, data=idToSend).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")


def stop_cloud_watch(ip):
    try:
        node_address = 'http://' + str(ip) + ':5001/stopStat'
        response = requests.post(url=node_address).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")


def clear_cache_stat(ip):
    try:
        node_address = 'http://' + str(ip) + ':5001/clearStats'
        response = requests.post(url=node_address).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")


@webapp.route('/remap', methods=['POST'])
def remap():
    num_node = int(request.form.get('num_node'))
    if num_node == memcache_mode['num_node']:
        value = {"success": "true"}
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
        return response
    # get all keys and images in the memcache
    key_list = {}
    response = None
    for id, ip in node_ip.items():
        if ip is not None:
            try:
                node_address = 'http://' + ip + ':5001/listKeys'
                response = requests.get(url=node_address).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")
            for key, item in response['content'].items():
                key_list[key] = item
            # clear cache before remap
            try:
                node_address = 'http://' + ip + ':5001/clearCache'
                response = requests.post(url=node_address).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")
    if memcache_mode['num_node'] > num_node:
        num_stop = memcache_mode['num_node'] - num_node
        for id, ip in node_ip.items():
            if ip is not None and num_stop > 0:
                node_ip[id] = None
                # stop cache
                stop_cloud_watch(ip)
                clear_cache_stat(ip)
                num_stop = num_stop - 1
        # send node_ip dict to localhost/5003/changeIP
        try:
            response = requests.post(url='http://localhost:5003/changeIP', data=node_ip).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Autoscaler loses connection")
    else:
        num_start = num_node - memcache_mode['num_node']
        session = boto3.Session(
            region_name=aws_config['region'],
            aws_access_key_id=aws_config['access_key_id'],
            aws_secret_access_key=aws_config['secret_access_key']
        )
        ec2 = session.resource('ec2')
        for id, ip in node_ip.items():
            if ip is None and num_start > 0:
                instance = ec2.Instance(id)
                public_ip = instance.public_ip_address
                node_ip[id] = public_ip
                num_start = num_start - 1
                schedule_cloud_watch(public_ip, id)
                # according to memcache_config, set config (send request to corresponding memcache)
                node_address = 'http://' + str(public_ip) + ':5001/setConfig'
                keyToSend = {'policy': memcache_config['policy'], 'size': memcache_config['capacity']}
                try:
                    response = requests.post(url=node_address, data=keyToSend).json()
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Cache loses connection")
        # send node_ip dict to localhost/5003/changeIP
        try:
            response = requests.post(url='http://localhost:5003/changeIP', data=node_ip).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Autoscaler loses connection")

    memcache_mode['num_node'] = num_node
    # sort key_list by time
    keys_to_sort = list(key_list.keys())
    if len(keys_to_sort) > 0:
        cursor = dbconnection.sort_by_time(keys_to_sort)
        for key in cursor:
            keyToSend = {'key': key[0]}
            try:
                response = requests.post(url='http://localhost:5002/map', data=keyToSend).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Manager app loses connection")

            node_address = 'http://' + response["content"] + ':5001/putImage'
            file = io.BytesIO(base64.b64decode(key_list[key[0]]))
            fileToSend = {'file': file}

            try:
                response = requests.post(url=node_address, data=keyToSend, files=fileToSend).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")
            if response is None or response["success"] == "false":
                webapp.logger.warning("Key: " + str(key) + "cannot remap to cache")
    webapp.logger.warning('remap finished')
    dbconnection.put_mode(memcache_mode['num_node'], memcache_mode['mode'], memcache_mode['max_thr'], memcache_mode['min_thr'], memcache_mode['expand_ratio'], memcache_mode['shrink_ratio'])
    try:
        requests.post(url='http://localhost:5003/setMode', data=memcache_mode)
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Autoscaler loses connection")
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response
