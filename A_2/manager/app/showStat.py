from flask import render_template, url_for, request, json
from app import webapp, memcache_mode, memcache_stat, node_ip
import requests
import datetime, timedelta
import boto3
from app.config import aws_config


@webapp.route('/showStat', methods=['GET'])
def showStat():
    return render_template("statistics.html", cursor=memcache_stat)

