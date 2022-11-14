from flask import Flask, request, json
from app import config
from app.config import aws_config
import requests
import boto3
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

global memcache_mode
global node_ip
global memcache_config
global memcache_stat

webapp = Flask(__name__)

memcache_mode = {'num_node': 1, 'mode': 'Manual', 'max_thr': 1, 'min_thr': 0, 'expand_ratio': 1, 'shrink_ratio': 1}
memcache_config = {'capacity': 128, 'policy': 'LRU'}
node_ip = {}
memcache_stat = {}
memcache_stat['Time'] = []
memcache_stat['NumItem'] = []
memcache_stat['TotalSize'] = []
memcache_stat['NumRequest'] = []
memcache_stat['HitRate'] = []
memcache_stat['MissRate'] = []

from app import main
from app import refreshConfiguration
from app import refreshMode
from app import showStat
from app import clear
from app import deleteAll
from app import putImage
from app import getKey
from app import map
from app import remap
from app import sizeChange


# TODO: need to call this when creating a new memcache instance
def schedule_cloud_watch(ip, id):
    try:
        node_address = 'http://' + str(ip) + ':5001/putStat'
        webapp.logger.warning(node_address)
        idToSend = {'InstanceId': id}
        response = requests.post(url=node_address, data=idToSend).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")


def monitor_stats():
    metric_names = ['NumItem', 'TotalSize', 'NumRequest', 'HitRate', 'MissRate']
    if len(memcache_stat['Time']) < 30:
        memcache_stat['Time'].append(datetime.now())
    else:
        memcache_stat['Time'].pop(0)
        memcache_stat['Time'].append(datetime.now())

    for metric in metric_names:

        value = get_stat(metric)

        if len(memcache_stat[metric]) < 30:
            memcache_stat[metric].append(value)
        else:
            memcache_stat[metric].pop(0)
            memcache_stat[metric].append(value)

    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


def get_stat(metric):
    client = boto3.client(
        'cloudwatch',
        aws_config['region'],
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key']
    )

    ts = datetime.utcnow()
    total = 0

    for id, ip in node_ip.items():
        value = client.get_metric_statistics(
            Period=60,
            Namespace='Memcache',
            MetricName=metric,
            Dimensions=[{'Name': 'NodeId', 'Value': str(id)}],
            StartTime=ts - timedelta(seconds=1 * 60),
            EndTime=ts,
            Statistics=['Average']
        )

        if not value['Datapoints']:
            webapp.logger.warning('No data for node ' + str(id) + ' at ' + str(ts))
        else:
            total += value['Datapoints'][0]['Average']

    if metric == 'HitRate' or metric == 'MissRate':
        return total / memcache_mode['num_node']
    else:
        return total


def initialize_instance():
    session = boto3.Session(
        region_name=aws_config['region'],
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key']
    )
    ec2 = session.resource('ec2')
    # pre-configured 8 nodes
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        node_ip[instance.instance_id] = None
    id = list(node_ip.keys())[0]
    instance = ec2.Instance(id)
    public_ip = instance.public_ip_address
    node_ip[id] = public_ip
    # send node_ip dict to localhost/5003/changeIP
    try:
        response = requests.post(url='http://localhost:5003/changeIP', data=node_ip).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Autoscaler loses connection")
    schedule_cloud_watch(public_ip, id)
    scheduler.add_job(id='monitor_stats', func=monitor_stats, trigger='interval', seconds=60)


initialize_instance()
