from flask import render_template, url_for, request, json
from app import webapp, memcache_mode, memcache_stat, node_ip
import requests
import datetime, timedelta
import boto3
from app.config import aws_config


@webapp.route('/showStat', methods=['GET'])
def showStat():
    return render_template("statistics.html", cursor=memcache_stat)


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