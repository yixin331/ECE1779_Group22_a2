from flask import render_template, redirect, url_for, request, json
from app import webapp, memcache_mode, node_ip, config, memcache_config
from app.config import aws_config
import requests
import base64
import io


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

    if memcache_mode['num_node'] > num_node:
        num_stop = memcache_mode['num_node'] - num_node
        id = list(node_ip.keys())[0:num_stop]
        # terminate instances
        ec2 = boto3.resource('ec2')
        ec2.instances.filter(InstanceIds=[id]).terminate()
        # remove key-value pair in node_ip
        for element in id:
            del node_ip[element]
        # maybe todo: call stopStat()
        # refer to schedule_cloud_watch(ip)
    else:
        num_start = num_node - memcache_mode['num_node']
        session = boto3.Session(
            region_name=aws_config['region'],
            aws_access_key_id=aws_config['access_key_id'],
            aws_secret_access_key=aws_config['secret_access_key']
        )
        ec2 = session.resource('ec2')
        USERDATA_SCRIPT = '''#!/bin/bash
            cd /home/ubuntu/ECE1779_Group22_a2/A_2/memcache
            pip install flask
            pip install apscheduler
            pip install boto3
            python3 run.py'''
        instances = ec2.create_instances(ImageId=config.ami_id, MinCount=1, MaxCount=num_start,
                                         InstanceType='t2.micro',
                                         UserData=USERDATA_SCRIPT)
        for instance in instances:
            instance_id = instance.instance_id
            webapp.logger.warning(instance_id)
            instance.wait_until_running()
            webapp.logger.warning('wait till instance is running')
            instance.reload()
            public_ip = instance.public_ip_address
            node_ip[instance_id] = public_ip
            # send node_ip dict to localhost/5003/changeIP
            nodeToSend = {"node": node_ip}
            try:
                response = requests.post(url='http://localhost:5003/changeIP', data=nodeToSend).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Autoscaling loses connection")
            webapp.logger.warning('wait till instance is ready')
            time.sleep(30)
            schedule_cloud_watch(public_ip, instance_id)
            # according to memcache_config, set config (send request to corresponding memcache)
            node_address = 'http://' + str(public_ip) + ':5001/setConfig'
            keyToSend = {'policy': memcache_config['policy'],'size': memcache_config['capacity']}
            try:
                response = requests.post(url=node_address, data=keyToSend).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")

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