from app import webapp, config
from app.config import aws_config
from flask import request, json
import requests
import base64
import io
import boto3
import os

@webapp.route('/ec2_create', methods=['POST'])
def ec2():
    session = boto3.Session(
        region_name=aws_config['region'],
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key']
    )
    ec2 = session.resource('ec2')
    # ec2_client = boto3.client(
    #     'ec2',
    #     region_name = aws_config['region'],
    #     aws_access_key_id = aws_config['access_key_id'],
    #     aws_secret_access_key = aws_config['secret_access_key']
    #
    USERDATA_SCRIPT = '''#!/bin/bash
    cd /home/ubuntu/ECE1779_Group22_a2/A_2/memcache
    pip install flask
    pip install apscheduler
    pip install boto3
    python3 run.py'''
    instances = ec2.create_instances(ImageId=config.ami_id, MinCount=1, MaxCount=1, InstanceType='t2.micro',
                                     UserData=USERDATA_SCRIPT)
    instance = instances[0]
    webapp.logger.warning('wait till instance is ready')
    instance.wait_until_running()
    instance.reload()
    public_ip = instance.public_ip_address
    instance_id = instance.instance_id
    webapp.logger.warning(public_ip)
    webapp.logger.warning(instance_id)

