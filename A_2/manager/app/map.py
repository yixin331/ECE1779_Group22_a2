from flask import render_template, redirect, url_for, request, json
from app import webapp, memcache_mode, node_ip
import requests
import hashlib


@webapp.route('/map', methods=['POST'])
def map():
    key = request.form.get('key')
    hash_val = hashlib.md5(key.encode()).hexdigest()
    hash_val = int(hash_val, base=16)
    index = hash_val % 16

    node_id = index % memcache_mode['num_node']
    instance_id = list(node_ip.keys())[node_id]
    ip_address = node_ip.get(instance_id)
    # active_list = []
    # for id, ip in node_ip.items():
    #     if not ip == None:
    #         active_list.append((id, ip))
    value = {"success": "true", "content": ip_address}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response