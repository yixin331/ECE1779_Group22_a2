from flask import render_template, redirect, url_for, request
from app import webapp

import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter

'''
    Part 1

    Modify the function ec2_list() so that only instances are displayed for the selected status

    Documentation for the EC2 filter function is available at:

    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

    Search in the above URL for the phrase "ec2.instances.filter"

    The filter function takes a very large number of options. The key that
    reflects the status of the instance is called "instance-state-name"

'''
# @webapp.route('/node_configure', methods=['GET'])
# def node_configure():
#     return render_template("configure/configure.html",title="Nodes Configure")


@webapp.route('/ec2_examples', methods=['GET', 'POST'])
# Display an HTML list of all ec2 instances
def ec2_list():
    status = request.form.get('filter', "")

    # create connection to ec2
    ec2 = boto3.resource('ec2')
    amount = 0
    if status == "" or status == "all":
        instances = ec2.instances.all()
        for i in instances:
            amount = amount + 1
        print("++++++++++++++++")
    else:  # status := pending | running | shutting-down | terminated | stopping | stopped

        ########### your code starts here  ################

        instances = ec2.instances.filter(
            Filters=
            [{
                'Name': 'instance-state-name',
                'Values': [status]}])

    ########### your code ends here    ################

    return render_template("ec2_examples/list.html", title="EC2 Instances", instances=instances, amount=amount)


@webapp.route('/ec2_examples/<id>', methods=['GET'])
# Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System

    namespace = 'AWS/EC2'
    statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []

    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute / 60
        cpu_stats.append([time, point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))

    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute / 60
        net_in_stats.append([time, point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))

    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute / 60
        net_out_stats.append([time, point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))

    return render_template("ec2_examples/view.html", title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)


@webapp.route('/ec2_examples/create', methods=['POST'])
# Start a new EC2 instance
def ec2_create():
    ec2 = boto3.resource('ec2')

    ec2.create_instances(ImageId=config.ami_id, MinCount=1, MaxCount=1,
                         InstanceType='t2.micro', SubnetId=config.subnet_id)

    return redirect(url_for('ec2_list'))


@webapp.route('/ec2_examples/delete/<id>', methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):
    # create connection to ec2
    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).terminate()

    return redirect(url_for('ec2_list'))
