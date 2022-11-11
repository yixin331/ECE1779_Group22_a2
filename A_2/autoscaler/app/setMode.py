from flask import request, json
from app import webapp, scheduler, memcache_mode, memcache_stat, node_ip
import requests
import datetime, timedelta
import boto3
from app.config import aws_config
import math


@webapp.route('/setMode', methods=['POST'])
def setMode():
    mode = request.form.get('mode')
    if mode == 'Manual':
        memcache_mode['num_node'] = request.form.get('num_node')
        if scheduler.get_job('monitor_stats'):
            scheduler.pause_job('monitor_stats')
    else:
        memcache_mode['num_node'] = request.form.get('num_node')
        memcache_mode['max_thr'] = request.form.get('max_thr')
        memcache_mode['min_thr'] = request.form.get('min_thr')
        memcache_mode['expand_ratio'] = request.form.get('expand_ratio')
        memcache_mode['shrink_ratio'] = request.form.get('shrink_ratio')
        monitor_stats()
        if scheduler.get_job('monitor_stats'):
            scheduler.resume_job('monitor_stats')
        else:
            scheduler.add_job(id='monitor_stats', func=monitor_stats, trigger='interval', seconds=60)

    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


def monitor_stats():
    metric_names = ['NumItem', 'TotalSize', 'NumRequest', 'HitRate', 'MissRate']
    num_node = memcache_mode['num_node']
    for metric in metric_names:

        value = get_stat(metric)

        if len(memcache_stat[metric]) < 30:
            memcache_stat[metric].append(value)
        else:
            memcache_stat[metric].pop(0)
            memcache_stat[metric].append(value)

        if metric == 'MissRate':
            if value > memcache_mode['max_thr']:
                num_node = min(math.floor(num_node) * memcache_mode['expand_ratio'], 8)
                dataToSend = {"num_node": num_node}
                try:
                    requests.post(url='http://localhost:5002/sizeChange', data=dataToSend)
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Manager loses connection")
            elif value < memcache_mode['min_thr']:
                num_node = max(math.ceil(num_node) * memcache_mode['shrink_ratio'], 1)
                dataToSend = {"num_node": num_node}
                try:
                    requests.post(url='http://localhost:5002/sizeChange', data=dataToSend)
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Manager loses connection")

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

    ts = datetime.now()
    total = 0



    for id, ip in node_ip.items():
        value = client.get_metric_statistics(
            Period=60,
            Namespace='Memcache',
            MetricName=metric,
            Dimensions=[{'Name': 'NodeId', 'Value': id}],
            StartTime=ts - timedelta(seconds=1 * 60),
            EndTime=ts,
            Statistics=['Average']
        )

        if not value['Datapoints']:
            webapp.logger.warning('No data for node ', id, 'at ' + ts)
        else:
            total += value['Datapoints'][0]['Average']

    if metric == 'HitRate' or metric == 'MissRate':
        return total / memcache_mode['num_node']
    else:
        return total


@webapp.route('/changeIP', methods=['POST'])
def changeIP():
    node_ip = request.form.get('node')

    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response
