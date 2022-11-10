from app import webapp, memcache_stat, node_id, scheduler
from flask import request, json, g
import boto3
from app.config import aws_config
from datetime import datetime


@webapp.route('/putStat', methods=['POST'])
def putStat():
    if scheduler.get_job('put_memcache_stat'):
        scheduler.resume_job('put_memcache_stat')
    else:
        scheduler.add_job(id='put_memcache_stat', func=put_memcache_stat, trigger='interval', seconds=5)
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


@webapp.route('/stopStat', methods=['POST'])
def stopStat():
    if scheduler.get_job('put_memcache_stat'):
        scheduler.pause_job('put_memcache_stat')
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


def put_memcache_stat():
    if memcache_stat['num_get'] == 0:
        send_metric_data(node_id, 'NumItem', memcache_stat['num_item'])
        send_metric_data(node_id, 'TotalSize', memcache_stat['total_size'])
        send_metric_data(node_id, 'NumRequest', memcache_stat['num_request'])
        send_metric_data(node_id, 'HitRate', 0)
        send_metric_data(node_id, 'MissRate', 0)
    else:
        send_metric_data(node_id, 'NumItem', memcache_stat['num_item'])
        send_metric_data(node_id, 'TotalSize', memcache_stat['total_size'])
        send_metric_data(node_id, 'NumRequest', memcache_stat['num_request'])
        send_metric_data(node_id, 'HitRate', (memcache_stat['num_get'] - memcache_stat['num_miss'])/memcache_stat['num_get'])
        send_metric_data(node_id, 'MissRate', memcache_stat['num_miss']/memcache_stat['num_get'])
    current_time = datetime.now()
    webapp.logger.warning('Sending metric data finished: ' + str(current_time))
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


def send_metric_data(node_id, metric_name, metric_value):
    client = boto3.client(
        'cloudwatch',
        aws_config['region'],
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key']
    )

    ts = datetime.now()
    response = client.put_metric_data(
        Namespace='Memcache',
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': 'NodeId',
                        'Value': str(node_id)
                    }
                ],
                'Value': metric_value,
                'Timestamp': ts,
                'StorageResolution': 1
            },
        ]
    )
    return response

