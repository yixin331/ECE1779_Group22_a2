from flask import render_template, redirect, url_for, request
from app import webapp, dbconnection, memcache_mode, node_ip, memcache_config
import requests
import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter


@webapp.route('/node_configure', methods=['GET','POST'])
def node_configure():
    return render_template("configure/configure.html")


@webapp.route('/refreshConfiguration', methods=['GET', 'POST'])
def refreshConfiguration():
    if request.method == 'GET':
        return render_template("configure.html")
    else:
        policy = request.form['policy']
        size = request.form['size']
        webapp.logger.warning(policy)
        webapp.logger.warning(size)
        memcache_config['capacity'] = int(size)
        memcache_config['policy'] = policy
        dataToSend = {"policy": policy, "size": size}
        response = None
        msg = ""
        for id, ip in node_ip.items():
            if not ip == None:
                # TODO: populate it to all memcache
                node_address = 'http://' + ip + ':5001/setConfig'
                try:
                    response = requests.post(url=node_address, data=dataToSend).json()
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Cache loses connection")
                if response is None:
                    msg = "Cache loses connection"
                elif response["success"] == "true":
                    msg = "Your cache has been reset"

        dbconnection.put_config(int(size), policy)
        return render_template("configure.html", result=msg,title="Resize Pool")