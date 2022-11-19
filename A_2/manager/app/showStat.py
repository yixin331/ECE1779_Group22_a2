from flask import render_template, url_for, request, json
from app import webapp, memcache_mode, memcache_stat, node_ip
import requests
import datetime, timedelta
import boto3
from app.config import aws_config


@webapp.route('/showStat', methods=['GET'])
def showStat():
    return render_template("statistics.html", cursor=memcache_stat)

@webapp.route('/pop', methods=['GET'])
def pop():
    messageToSend = {'message': 'themessage'}
    response = requests.post(url='http://35.170.186.67:5000/pop', data=messageToSend).json()
    return render_template("main.html",title="Manager APP")

